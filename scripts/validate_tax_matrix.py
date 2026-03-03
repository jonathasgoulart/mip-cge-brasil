import json
import numpy as np

def run_tests():
    """Validation test suite for disaggregated tax matrix"""
    
    print("="*70)
    print("TAX MATRIX VALIDATION TEST SUITE (2021)")
    print("="*70)
    
    # Load data
    with open('output/tax_data.json', 'r') as f:
        data = json.load(f)
    
    X = np.array(data['production_X'])
    taxes_by_type = {k: np.array(v) for k, v in data['taxes_by_type'].items()}
    coef_by_type = {k: np.array(v) for k, v in data['coef_by_type'].items()}
    targets = data['metadata']['targets']
    
    # Load sector names
    import csv
    names = []
    with open('data/processed/mip_2015/05.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 4: continue
            if i >= 4 + 67: break
            names.append(row[1])
    
    test_results = []
    
    # TEST 1: Total Integrity
    print("\n[TEST 1] Total Sum Integrity")
    print("-" * 70)
    total_distributed = sum(np.sum(v) for v in taxes_by_type.values())
    target_total = sum(targets.values())
    diff_pct = abs(total_distributed - target_total) / target_total * 100
    
    print(f"Target Total:      R$ {target_total:,.0f} M")
    print(f"Distributed Total: R$ {total_distributed:,.0f} M")
    print(f"Difference:        {diff_pct:.2f}%")
    
    passed = diff_pct < 1.0
    test_results.append(("Total Integrity", passed))
    print(f"Status: {'[PASS]' if passed else '[FAIL]'}")
    
    # TEST 2: Individual Tax Targets
    print("\n[TEST 2] Individual Tax Targets")
    print("-" * 70)
    for tax_type, target in targets.items():
        actual = np.sum(taxes_by_type[tax_type])
        diff = abs(actual - target) / target * 100 if target > 0 else 0
        passed = diff < 1.0
        test_results.append((f"{tax_type} Target", passed))
        print(f"{tax_type:12s}: Target={target:>10,.0f} | Actual={actual:>10,.0f} | Diff={diff:>5.2f}% {'[OK]' if passed else '[X]'}")
    
    # TEST 3: Sector Logic - IPI (should be zero for services)
    print("\n[TEST 3] IPI Logic (Zero for Services)")
    print("-" * 70)
    service_sectors = [i for i, name in enumerate(names) if i >= 43]
    ipi_in_services = np.sum(taxes_by_type['IPI'][service_sectors])
    passed = ipi_in_services < 100  # Tolerance of 100M
    test_results.append(("IPI in Services = 0", passed))
    print(f"IPI in Service Sectors: R$ {ipi_in_services:,.0f} M")
    print(f"Status: {'[PASS]' if passed else '[FAIL]'}")
    
    # TEST 4: Sector Logic - ISS (should be zero for manufacturing)
    print("\n[TEST 4] ISS Logic (Zero for Manufacturing)")
    print("-" * 70)
    manuf_sectors = [i for i in range(6, 39)]
    iss_in_manuf = np.sum(taxes_by_type['ISS'][manuf_sectors])
    passed = iss_in_manuf < 100
    test_results.append(("ISS in Manufacturing = 0", passed))
    print(f"ISS in Manufacturing: R$ {iss_in_manuf:,.0f} M")
    print(f"Status: {'[PASS]' if passed else '[FAIL]'}")
    
    # TEST 5: Maximum Tax Rate Check
    print("\n[TEST 5] Maximum Tax Rate (< 50%)")
    print("-" * 70)
    total_coef = data['coef_tax_total']
    max_rate = max(total_coef) * 100
    max_sector_idx = np.argmax(total_coef)
    passed = max_rate < 50
    test_results.append(("Max Rate < 50%", passed))
    print(f"Maximum Rate: {max_rate:.2f}% in sector '{names[max_sector_idx][:40]}'")
    print(f"Status: {'[PASS]' if passed else '[FAIL]'}")
    
    # TEST 6: Top Tax-Paying Sectors (Reality Check)
    print("\n[TEST 6] Top 5 Tax-Paying Sectors (Reality Check)")
    print("-" * 70)
    total_taxes = np.array(data['taxes_total_abs'])
    top_5_idx = np.argsort(total_taxes)[-5:][::-1]
    
    print("Sector Name                                  | Total Tax (M) | Rate")
    print("-" * 70)
    for idx in top_5_idx:
        rate = (total_taxes[idx] / X[idx]) * 100 if X[idx] > 0 else 0
        print(f"{names[idx][:44]:44s} | {total_taxes[idx]:>13,.0f} | {rate:>5.2f}%")
    
    # Expected high-tax sectors: Fuels, Beverages, Vehicles
    expected_high = ["COMBUSTÍVEL", "BEBIDA", "AUTOMÓVEL", "PETRÓLEO", "TABACO"]
    found_expected = sum(1 for idx in top_5_idx if any(e in names[idx].upper() for e in expected_high))
    passed = found_expected >= 2
    test_results.append(("Top sectors realistic", passed))
    print(f"\nExpected high-tax sectors found: {found_expected}/5")
    print(f"Status: {'[PASS]' if passed else '[FAIL]'}")
    
    # TEST 7: ICMS Concentration (should be highest)
    print("\n[TEST 7] ICMS as Largest Tax Component")
    print("-" * 70)
    tax_totals = {k: np.sum(v) for k, v in taxes_by_type.items()}
    largest = max(tax_totals, key=tax_totals.get)
    passed = largest == "ICMS"
    test_results.append(("ICMS is largest", passed))
    print(f"Largest tax component: {largest} (R$ {tax_totals[largest]:,.0f} M)")
    print(f"Status: {'[PASS]' if passed else '[FAIL]'}")
    
    # SUMMARY
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    total_tests = len(test_results)
    passed_tests = sum(1 for _, p in test_results if p)
    
    for test_name, passed in test_results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name:40s}: {status}")
    
    print("-" * 70)
    print(f"Total: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n[SUCCESS] ALL TESTS PASSED! Tax matrix is validated.")
    else:
        print(f"\n[WARNING] {total_tests - passed_tests} test(s) failed. Review required.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    run_tests()
