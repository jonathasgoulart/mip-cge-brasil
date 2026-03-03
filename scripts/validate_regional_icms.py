import json
import numpy as np

def validate_regional_icms():
    """
    Run comprehensive validation tests on regional ICMS matrix
    """
    
    print("="*70)
    print("REGIONAL ICMS VALIDATION SUITE")
    print("="*70)
    
    # Load results
    with open('output/icms_regional_full.json', 'r', encoding='utf-8') as f:
        regional = json.load(f)
    
    with open('output/tax_data.json', 'r', encoding='utf-8') as f:
        nacional = json.load(f)
    
    icms_nacional = np.array(nacional['taxes_by_type']['ICMS'])
    total_target = np.sum(icms_nacional)
    
    tests_passed = 0
    tests_total = 0
    
    # ========================================================================
    # TEST 1: MASS CONSERVATION
    # ========================================================================
    
    tests_total += 1
    print(f"\n[Test 1/4] Mass Conservation")
    print("-"*70)
    
    total_calculated = regional['total_icms_milhoes']
    deviation_pct = abs(total_calculated - total_target) / total_target * 100
    
    print(f"  Target (CTB 2021): R$ {total_target/1e3:.2f} Bi")
    print(f"  Calculated:        R$ {total_calculated/1e3:.2f} Bi")
    print(f"  Deviation:         {deviation_pct:.6f}%")
    
    if deviation_pct < 0.01:
        print(f"  Status: PASS")
        tests_passed += 1
    else:
        print(f"  Status: FAIL (tolerance: 0.01%)")
    
    # ========================================================================
    # TEST 2: SECTORAL CONSISTENCY
    # ========================================================================
    
    tests_total += 1
    print(f"\n[Test 2/4] Sectoral Consistency")
    print("-"*70)
    
    max_sectoral_deviation = 0
    failed_sectors = []
    
    for sector_id, uf_values in regional['by_sector_by_uf'].items():
        sector_total = sum(uf_values.values())
        sector_idx = int(sector_id.split('_')[1]) - 1
        sector_target = icms_nacional[sector_idx]
        
        if sector_target > 0:
            deviation = abs(sector_total - sector_target) / sector_target * 100
            max_sectoral_deviation = max(max_sectoral_deviation, deviation)
            
            if deviation > 5.0:
                failed_sectors.append((sector_id, deviation))
    
    print(f"  Max sectoral deviation: {max_sectoral_deviation:.2f}%")
    print(f"  Sectors outside tolerance (>5%): {len(failed_sectors)}")
    
    if len(failed_sectors) == 0:
        print(f"  Status: PASS")
        tests_passed += 1
    else:
        print(f"  Status: FAIL")
        print(f"  Failed sectors: {failed_sectors[:3]}")
    
    # ========================================================================
    # TEST 3: REGIONAL COHERENCE
    # ========================================================================
    
    tests_total += 1
    print(f"\n[Test 3/4] Regional Coherence")
    print("-"*70)
    
    # Check if high-factor states have proportionally higher ICMS
    sp_factor = regional['by_uf']['SP']['regional_factor']
    ap_factor = regional['by_uf']['AP']['regional_factor']
    
    sp_share = regional['by_uf']['SP']['share_pct']
    ap_share = regional['by_uf']['AP']['share_pct']
    
    print(f"  SP: Factor={sp_factor:.2f}x, Share={sp_share:.1f}%")
    print(f"  AP: Factor={ap_factor:.2f}x, Share={ap_share:.2f}%")
    
    # SP should have much higher share than AP
    coherence_check = sp_share > 10 * ap_share
    
    if coherence_check:
        print(f"  Status: PASS (SP share >> AP share)")
        tests_passed += 1
    else:
        print(f"  Status: FAIL")
    
    # ========================================================================
    # TEST 4: ECONOMIC SANITY
    # ========================================================================
    
    tests_total += 1
    print(f"\n[Test 4/4] Economic Sanity")
    print("-"*70)
    
    all_coefficients = []
    for uf, coefs in regional['coefficients'].items():
        all_coefficients.extend([c for c in coefs if c > 0])
    
    all_coefficients = np.array(all_coefficients)
    
    min_coef = np.min(all_coefficients) if len(all_coefficients) > 0 else 0
    max_coef = np.max(all_coefficients) if len(all_coefficients) > 0 else 0
    mean_coef = np.mean(all_coefficients) if len(all_coefficients) > 0 else 0
    
    print(f"  Min coefficient: {min_coef*100:.2f}%")
    print(f"  Max coefficient: {max_coef*100:.2f}%")
    print(f"  Mean coefficient: {mean_coef*100:.2f}%")
    
    # Check bounds
    sanity_check = (min_coef >= 0) and (max_coef <= 0.30) and (mean_coef > 0)
    
    if sanity_check:
        print(f"  Status: PASS (all within 0-30% range)")
        tests_passed += 1
    else:
        print(f"  Status: FAIL")
    
    # ========================================================================
    # FINAL REPORT
    # ========================================================================
    
    print(f"\n{'='*70}")
    print(f"VALIDATION SUMMARY")
    print("="*70)
    print(f"\nTests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print(f"Status: ALL TESTS PASSED")
    else:
        print(f"Status: {tests_total - tests_passed} TEST(S) FAILED")
    
    print(f"\n{'='*70}\n")
    
    # Save validation results
    validation_results = {
        "validation_date": "2024-01-24",
        "tests_total": tests_total,
        "tests_passed": tests_passed,
        "tests": {
            "mass_conservation": {
                "passed": deviation_pct < 0.01,
                "deviation_pct": float(deviation_pct)
            },
            "sectoral_consistency": {
                "passed": len(failed_sectors) == 0,
                "max_deviation_pct": float(max_sectoral_deviation)
            },
            "regional_coherence": {
                "passed": coherence_check
            },
            "economic_sanity": {
                "passed": sanity_check,
                "mean_coefficient_pct": float(mean_coef * 100),
                "max_coefficient_pct": float(max_coef * 100)
            }
        }
    }
    
    with open('output/icms_regional_validation.json', 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"Validation report saved: output/icms_regional_validation.json\n")
    
    return tests_passed == tests_total

if __name__ == "__main__":
    validate_regional_icms()
