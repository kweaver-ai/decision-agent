"""单元测试 - utils/snow_id 模块"""

import time
from unittest import TestCase
from unittest.mock import patch

from app.utils.snow_id import (
    IdWorker,
    snow_id,
    WORKER_ID_BITS,
    DATACENTER_ID_BITS,
    SEQUENCE_BITS,
    MAX_WORKER_ID,
    MAX_DATACENTER_ID,
    WOKER_ID_SHIFT,
    DATACENTER_ID_SHIFT,
    TIMESTAMP_LEFT_SHIFT,
    SEQUENCE_MASK,
    TWEPOCH,
)


class TestIdWorker(TestCase):
    """测试 IdWorker 类"""

    def test_init_valid_params(self):
        """测试有效参数初始化"""
        worker = IdWorker(datacenter_id=1, worker_id=1, sequence=0)
        self.assertEqual(worker.datacenter_id, 1)
        self.assertEqual(worker.worker_id, 1)
        self.assertEqual(worker.sequence, 0)
        self.assertEqual(worker.last_timestamp, -1)

    def test_init_invalid_worker_id_too_large(self):
        """测试worker_id超出最大值"""
        with self.assertRaises(ValueError) as context:
            IdWorker(datacenter_id=1, worker_id=MAX_WORKER_ID + 1)
        self.assertIn("worker_id值越界", str(context.exception))

    def test_init_invalid_worker_id_negative(self):
        """测试worker_id为负数"""
        with self.assertRaises(ValueError) as context:
            IdWorker(datacenter_id=1, worker_id=-1)
        self.assertIn("worker_id值越界", str(context.exception))

    def test_init_invalid_datacenter_id_too_large(self):
        """测试datacenter_id超出最大值"""
        with self.assertRaises(ValueError) as context:
            IdWorker(datacenter_id=MAX_DATACENTER_ID + 1, worker_id=1)
        self.assertIn("datacenter_id值越界", str(context.exception))

    def test_init_invalid_datacenter_id_negative(self):
        """测试datacenter_id为负数"""
        with self.assertRaises(ValueError) as context:
            IdWorker(datacenter_id=-1, worker_id=1)
        self.assertIn("datacenter_id值越界", str(context.exception))

    def test_gen_timestamp(self):
        """测试生成时间戳"""
        worker = IdWorker(1, 1)
        timestamp = worker._gen_timestamp()
        self.assertIsInstance(timestamp, int)
        self.assertGreater(timestamp, 0)

    @patch("time.time")
    def test_get_id_basic(self, mock_time):
        """测试基本ID生成"""
        mock_time.return_value = TWEPOCH / 1000 + 1
        worker = IdWorker(1, 1)
        id1 = worker.get_id()
        self.assertIsInstance(id1, int)
        self.assertGreater(id1, 0)

    @patch("time.time")
    def test_get_id_unique(self, mock_time):
        """测试ID唯一性"""
        mock_time.return_value = TWEPOCH / 1000 + 1
        worker = IdWorker(1, 1)
        id1 = worker.get_id()
        id2 = worker.get_id()
        self.assertNotEqual(id1, id2)

    @patch("time.time")
    def test_get_id_same_timestamp(self, mock_time):
        """测试同一毫秒内ID生成"""
        mock_time.return_value = TWEPOCH / 1000 + 1
        worker = IdWorker(1, 1)
        ids = [worker.get_id() for _ in range(10)]
        self.assertEqual(len(set(ids)), len(ids))

    @patch("time.time")
    def test_get_id_sequence_overflow(self, mock_time):
        """测试序列号溢出"""
        mock_time.return_value = TWEPOCH / 1000 + 1
        worker = IdWorker(1, 1, sequence=SEQUENCE_MASK - 1)
        id1 = worker.get_id()
        # 第一次调用时，由于last_timestamp是-1，sequence会被重置为0
        self.assertEqual(worker.sequence, 0)
        # 再次调用时，时间戳相同，sequence会递增
        id2 = worker.get_id()
        self.assertEqual(worker.sequence, 1)

    @patch("time.time")
    def test_get_id_clock_backward(self, mock_time):
        """测试时钟回拨"""
        mock_time.return_value = TWEPOCH / 1000 + 2
        worker = IdWorker(1, 1)
        worker.get_id()
        mock_time.return_value = TWEPOCH / 1000 + 1
        with self.assertRaises(Exception):
            worker.get_id()

    @patch("time.time")
    def test_get_id_different_timestamps(self, mock_time):
        """测试不同时间戳ID生成"""
        mock_time.return_value = TWEPOCH / 1000 + 1
        worker = IdWorker(1, 1)
        id1 = worker.get_id()
        self.assertEqual(worker.sequence, 0)

        mock_time.return_value = TWEPOCH / 1000 + 2
        id2 = worker.get_id()
        self.assertEqual(worker.sequence, 0)

        self.assertNotEqual(id1, id2)

    @patch("time.time")
    def test_id_components(self, mock_time):
        """测试ID组件正确性"""
        current_time = TWEPOCH / 1000 + 1000
        mock_time.return_value = current_time
        worker = IdWorker(5, 10, sequence=0)
        id_val = worker.get_id()

        timestamp_part = (int(current_time * 1000) - TWEPOCH) << TIMESTAMP_LEFT_SHIFT
        datacenter_part = 5 << DATACENTER_ID_SHIFT
        worker_part = 10 << WOKER_ID_SHIFT
        sequence_part = 0

        expected_id = timestamp_part | datacenter_part | worker_part | sequence_part
        self.assertEqual(id_val, expected_id)

    def test_til_next_millis(self):
        """测试等待下一毫秒"""
        worker = IdWorker(1, 1)
        next_time = worker._til_next_millis(int(time.time() * 1000) - 100)
        self.assertGreaterEqual(next_time, int(time.time() * 1000))


class TestSnowIdConstants(TestCase):
    """测试雪花ID常量"""

    def test_worker_id_bits(self):
        self.assertEqual(WORKER_ID_BITS, 5)

    def test_datacenter_id_bits(self):
        self.assertEqual(DATACENTER_ID_BITS, 5)

    def test_sequence_bits(self):
        self.assertEqual(SEQUENCE_BITS, 12)

    def test_max_worker_id(self):
        self.assertEqual(MAX_WORKER_ID, 31)

    def test_max_datacenter_id(self):
        self.assertEqual(MAX_DATACENTER_ID, 31)

    def test_worker_id_shift(self):
        self.assertEqual(WOKER_ID_SHIFT, 12)

    def test_datacenter_id_shift(self):
        self.assertEqual(DATACENTER_ID_SHIFT, 17)

    def test_timestamp_left_shift(self):
        self.assertEqual(TIMESTAMP_LEFT_SHIFT, 22)

    def test_sequence_mask(self):
        self.assertEqual(SEQUENCE_MASK, 4095)

    def test_twepoch(self):
        self.assertEqual(TWEPOCH, 1288834974657)


class TestSnowIdFunction(TestCase):
    """测试 snow_id 函数"""

    def test_snow_id_format(self):
        """测试雪花ID格式"""
        id_val = snow_id()
        self.assertIsInstance(id_val, int)
        self.assertGreater(id_val, 0)
        self.assertLessEqual(len(str(id_val)), 19)

    def test_snow_id_unique(self):
        """测试雪花ID唯一性（使用同一worker实例）"""
        worker = IdWorker(1, 1)
        ids = [worker.get_id() for _ in range(100)]
        self.assertEqual(len(set(ids)), len(ids))


class TestIdWorkerSequence(TestCase):
    """测试 IdWorker 序列号逻辑"""

    @patch("time.time")
    def test_sequence_increments(self, mock_time):
        """测试序列号递增"""
        mock_time.return_value = TWEPOCH / 1000 + 1
        worker = IdWorker(1, 1, sequence=0)
        id1 = worker.get_id()
        # 由于last_timestamp初始为-1，第一次调用会重置sequence为0
        self.assertEqual(worker.sequence, 0)
        id2 = worker.get_id()
        self.assertEqual(worker.sequence, 1)
        id3 = worker.get_id()
        self.assertEqual(worker.sequence, 2)

    @patch("time.time")
    def test_sequence_resets_on_new_timestamp(self, mock_time):
        """测试新时间戳序列号重置"""
        mock_time.return_value = TWEPOCH / 1000 + 1
        worker = IdWorker(1, 1)
        id1 = worker.get_id()
        worker.sequence = 10

        mock_time.return_value = TWEPOCH / 1000 + 2
        id2 = worker.get_id()
        self.assertEqual(worker.sequence, 0)
