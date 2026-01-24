package daconfvalobj

import (
	"testing"
)

func TestAugment_DataSource_ValObjCheck(t *testing.T) {
	validKg := KgSource{
		KgID:    "kg1",
		Fields:   []string{"field1", "field2"},
	}
	invalidKg := KgSource{
		KgID: "kg-invalid",
	}

	tests := []struct {
		name    string
		ads     *AugmentDataSource
		wantErr bool
	}{
		{
			name: "有效的Kg配置",
			ads: &AugmentDataSource{
				Kg: []KgSource{validKg},
			},
			wantErr: false,
		},
		{
			name:    "空的Kg列表",
			ads:     &AugmentDataSource{},
			wantErr: true,
		},
		{
			name: "Kg包含无效项",
			ads: &AugmentDataSource{
				Kg: []KgSource{invalidKg},
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.ads.ValObjCheck()
			if tt.wantErr {
				t.Errorf("ValObjCheck() error = %v, want error", err)
			} else {
				if err != nil {
					t.Errorf("ValObjCheck() unexpected error: %v", err)
				}
			}
		})
	}
}
