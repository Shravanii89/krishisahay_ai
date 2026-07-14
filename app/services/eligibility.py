def calculate_eligibility(user, scheme):
    """
    Evaluates a farmer's eligibility for a given scheme based on rules.
    
    Returns a dict with:
      - is_eligible (bool): True if matches all strict requirements.
      - score (int): A percentage showing how close the match is.
      - reasons (list of str): List of criteria met.
      - gaps (list of str): List of criteria not met.
    """
    reasons = []
    gaps = []
    
    # Track critical rules
    total_checks = 0
    passed_checks = 0
    
    # 1. State Check (State-specific schemes)
    if scheme.state_specific and scheme.state_specific.lower() != 'all':
        total_checks += 1
        if user.state.lower() == scheme.state_specific.lower():
            passed_checks += 1
            reasons.append(f"Located in target state: {scheme.state_specific}")
        else:
            gaps.append(f"Scheme is only for farmers in {scheme.state_specific}. You are in {user.state}.")
    
    # 2. Age Check
    if scheme.min_age and scheme.min_age > 0:
        total_checks += 1
        if user.age >= scheme.min_age:
            passed_checks += 1
            reasons.append(f"Age {user.age} meets minimum requirement of {scheme.min_age} years")
        else:
            gaps.append(f"Requires minimum age of {scheme.min_age} years. You are {user.age}.")
            
    # 3. Land Size Check
    if scheme.max_land_size is not None:
        total_checks += 1
        if user.land_size <= scheme.max_land_size:
            passed_checks += 1
            reasons.append(f"Land size of {user.land_size} hectares is within the limit of {scheme.max_land_size} hectares")
        else:
            gaps.append(f"Requires land size less than or equal to {scheme.max_land_size} hectares. Your land size is {user.land_size} hectares.")
            
    # 4. Annual Income Check
    if scheme.max_income is not None:
        total_checks += 1
        if user.annual_income <= scheme.max_income:
            passed_checks += 1
            reasons.append(f"Annual income of ₹{user.annual_income:,.2f} is within limit of ₹{scheme.max_income:,.2f}")
        else:
            gaps.append(f"Requires annual income less than or equal to ₹{scheme.max_income:,.2f}. Your income is ₹{user.annual_income:,.2f}.")
            
    # 5. Crop Type Check
    scheme_crops = scheme.get_crops_list()
    if scheme_crops:
        total_checks += 1
        user_crops = [c.lower().strip() for c in user.get_crops_list()]
        
        # Check if there's any overlap between user's crops and required crops
        overlap = set(user_crops).intersection(set(scheme_crops))
        
        if overlap:
            passed_checks += 1
            reasons.append(f"Grower of target crop(s): {', '.join(overlap).capitalize()}")
        else:
            gaps.append(f"Scheme is designated for crops: {', '.join(scheme_crops).capitalize()}. You grow: {', '.join(user_crops).capitalize()}.")
            
    # 6. Target Category Check
    if scheme.target_category and scheme.target_category.lower() != 'all':
        total_checks += 1
        tc = scheme.target_category.lower()
        
        # Demographic Check
        if tc == 'sc/st':
            if user.category in ['SC', 'ST']:
                passed_checks += 1
                reasons.append(f"Belongs to target demographic: {user.category}")
            else:
                gaps.append(f"Scheme is targeted for SC/ST category. Your category is {user.category}.")
        elif tc == 'women':
            # Note: Assuming 'Women' was an option or we just do a generic check, for now we will just check if user.category == 'Women' (though not in our form, just for future proofing)
            if user.category.lower() == 'women':
                passed_checks += 1
                reasons.append("Belongs to target demographic: Women")
            else:
                gaps.append(f"Scheme is targeted for Women farmers.")
        elif tc == 'small/marginal':
            # Check derived farmer scale
            if user.land_size <= 2.0:
                passed_checks += 1
                scale = "Marginal" if user.land_size <= 1.0 else "Small"
                reasons.append(f"Qualifies as {scale} farmer (Land size: {user.land_size} Ha)")
            else:
                gaps.append(f"Targeted for Small/Marginal farmers (≤ 2.0 Ha). Your land size is {user.land_size} Ha.")
        else:
            # Exact match fallback
            if user.category.lower() == tc:
                passed_checks += 1
                reasons.append(f"Belongs to target demographic: {user.category}")
            else:
                gaps.append(f"Scheme is targeted for {scheme.target_category}. Your category is {user.category}.")

    # If there are no specific rules, the farmer is eligible
    if total_checks == 0:
        is_eligible = True
        score = 100
        reasons.append("Open to all Indian farmers with no specific eligibility restrictions.")
    else:
        is_eligible = (len(gaps) == 0)
        score = int((passed_checks / total_checks) * 100)
        
    return {
        'is_eligible': is_eligible,
        'score': score,
        'reasons': reasons,
        'gaps': gaps
    }


def get_recommendations(user, schemes):
    """
    Returns a sorted list of eligible and partially eligible schemes for a user.
    """
    eligible_schemes = []
    partially_eligible_schemes = []
    
    for scheme in schemes:
        result = calculate_eligibility(user, scheme)
        scheme_info = {
            'scheme': scheme,
            'is_eligible': result['is_eligible'],
            'score': result['score'],
            'reasons': result['reasons'],
            'gaps': result['gaps']
        }
        
        if result['is_eligible']:
            eligible_schemes.append(scheme_info)
        elif result['score'] > 0: # has at least one matching criterion
            partially_eligible_schemes.append(scheme_info)
            
    # Sort eligible schemes by score (highest first), then by id
    eligible_schemes.sort(key=lambda x: x['score'], reverse=True)
    # Sort partially eligible by score (highest first)
    partially_eligible_schemes.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'eligible': eligible_schemes,
        'partially_eligible': partially_eligible_schemes
    }
