import asyncio
from typing import AsyncGenerator, Dict, Optional

from anyio import CancelScope

from app.logic.agent_core_logic_v2.agent_core_v2 import AgentCoreV2
from app.logic.agent_core_logic_v2.agent_cache_manage_logic import AgentCacheManager
from app.domain.vo.agentvo import AgentConfigVo, AgentInputVo
from app.domain.vo.agent_cache import AgentCacheIdVO
from app.domain.constant import AGENT_CACHE_TTL, AGENT_CACHE_DATA_UPDATE_PASS_SECOND
from app.common.stand_log import StandLogger

# 全局AgentCacheManager实例
cache_manager = AgentCacheManager()


async def check_and_update_cache(
    cache_id_vo: AgentCacheIdVO,
    agent_config: AgentConfigVo,
    headers: Dict[str, str],
    account_id: str,
    account_type: str,
) -> None:
    """检查并更新缓存
    
    根据缓存的TTL状态决定是创建新缓存还是更新已有缓存：
    - TTL <= 0: 缓存不存在或已过期，创建新缓存
    - TTL > 0 且已过时间 >= 阈值: 更新缓存数据
    - TTL > 0 且已过时间 < 阈值: 无需更新
    
    Args:
        cache_id_vo: 缓存ID值对象
        agent_config: Agent配置
        headers: HTTP请求头
        account_id: 账户ID
        account_type: 账户类型
    """
    try:
        current_ttl = await cache_manager.cache_service.get_ttl(cache_id_vo)
        
        # 缓存不存在或已过期 (TTL <= 0)
        if current_ttl <= 0:
            StandLogger.debug(
                f"[check_and_update_cache] 缓存不存在或已过期: cache_id={cache_id_vo}, TTL={current_ttl}, 创建新缓存"
            )
            await cache_manager.create_cache(
                account_id=account_id,
                account_type=account_type,
                agent_id=cache_id_vo.agent_id,
                agent_version=cache_id_vo.agent_version,
                agent_config=agent_config,
                headers=headers,
            )
            new_ttl = await cache_manager.cache_service.get_ttl(cache_id_vo)
            StandLogger.debug(
                f"[check_and_update_cache] ✅ 缓存创建完成: cache_id={cache_id_vo}, 新TTL={new_ttl}秒"
            )
        else:
            # 缓存存在，检查是否需要更新
            ttl_passed = AGENT_CACHE_TTL - current_ttl
            StandLogger.debug(
                f"[check_and_update_cache] 缓存TTL检查: cache_id={cache_id_vo}, "
                f"原始TTL={AGENT_CACHE_TTL}秒, 当前TTL={current_ttl}秒, 已过={ttl_passed}秒, "
                f"阈值={AGENT_CACHE_DATA_UPDATE_PASS_SECOND}秒"
            )

            # 如果 TTL 减少超过阈值，触发缓存更新
            if ttl_passed >= AGENT_CACHE_DATA_UPDATE_PASS_SECOND:
                StandLogger.debug(
                    f"[check_and_update_cache] 🔄 触发缓存更新: cache_id={cache_id_vo}, ttl_passed={ttl_passed}秒"
                )
                await cache_manager.update_cache_data(
                    cache_id_vo=cache_id_vo,
                    agent_config=agent_config,
                    headers=headers,
                )
                new_ttl = await cache_manager.cache_service.get_ttl(cache_id_vo)
                StandLogger.debug(
                    f"[check_and_update_cache] ✅ 缓存更新完成: cache_id={cache_id_vo}, 新TTL={new_ttl}秒"
                )
            else:
                StandLogger.debug(
                    f"[check_and_update_cache] ⏳ 无需更新缓存: ttl_passed={ttl_passed}秒 < 阈值={AGENT_CACHE_DATA_UPDATE_PASS_SECOND}秒"
                )
    except Exception as e:
        StandLogger.error(f"[check_and_update_cache] ❌ 缓存更新检查失败: {e}")


async def create_safe_output_generator(
    agent_core_v2: AgentCoreV2,
    agent_config: AgentConfigVo,
    agent_input: AgentInputVo,
    headers: Dict[str, str],
    is_debug_run: bool,
    start_time: float,
    cache_id_vo: Optional[AgentCacheIdVO] = None,
    account_id: str = "",
    account_type: str = "",
) -> AsyncGenerator[str, None]:
    """
    包装输出生成器，安全处理客户端断开连接的情况

    Args:
        agent_core_v2: Agent核心实例
        agent_config: Agent配置
        agent_input: Agent输入
        headers: 请求头
        is_debug_run: 是否为调试模式
        start_time: 开始时间
        cache_id_vo: 缓存ID值对象（用于检查是否需要更新缓存）
        account_id: 账户ID
        account_type: 账户类型
    """

    # 1. 获得generator
    output_generator = agent_core_v2.output_handler.result_output(
        agent_config, agent_input, headers, is_debug_run, start_time=start_time
    )

    closed = False

    # 2. 遍历generator
    try:
        async for chunk in output_generator:
            yield chunk
        closed = True
    except GeneratorExit:
        # 客户端断开连接，保持异常向外传播
        raise
    except asyncio.CancelledError:
        StandLogger.info("Client cancelled stream")
        raise
    except Exception as e:
        StandLogger.error(f"Output generator error: {e}")
        raise
    finally:
        if not closed:
            try:
                with CancelScope(shield=True):
                    await output_generator.aclose()
            except StopAsyncIteration:
                pass
            except Exception as close_err:
                StandLogger.warn(
                    f"Failed to close output generator gracefully: {close_err}"
                )

        # 3. 检查是否需要更新缓存（无论流是否正常结束都进行检查）
        if cache_id_vo:
            await check_and_update_cache(
                cache_id_vo=cache_id_vo,
                agent_config=agent_config,
                headers=headers,
                account_id=account_id,
                account_type=account_type,
            )
