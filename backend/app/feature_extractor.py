def extract_features(tree_json):
    features = {
        "has_readme": False,
        "has_requirements": False,
        "has_dockerfile": False,
        "has_ci_cd": False
    }

    if "tree" not in tree_json:
        return features

    for item in tree_json["tree"]:
        path = item["path"].lower()

        if "readme" in path:
            features["has_readme"] = True

        if "requirements.txt" in path:
            features["has_requirements"] = True

        if "dockerfile" in path:
            features["has_dockerfile"] = True

        if ".github/workflows" in path:
            features["has_ci_cd"] = True

    return features
