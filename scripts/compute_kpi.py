import json, time
from collections import Counter

# One deliberately simple, deliberately editable KPI definition -- change
# TARGET_SKILL, or write a different KPI function entirely. Per this course's
# standing principle: a KPI is a construct you chose, not a neutral fact.
TARGET_SKILL = "python"

def load_extracted(path="data/extracted.json"):
    with open(path) as f:
        return json.load(f)["postings"]

def compute_kpi(postings, target_skill=TARGET_SKILL):
    n = len(postings)
    matching = [
        p for p in postings
        if any(target_skill.lower() in s.lower() for s in p.get("required_skills", []))
    ]
    all_skills = Counter()
    for p in postings:
        for s in p.get("required_skills", []):
            all_skills[s] += 1

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kpi_label": f"% of postings mentioning '{target_skill}'",
        "kpi_value": round(len(matching) / n, 3) if n else 0.0,
        "n_postings_analyzed": n,
        "n_matching": len(matching),
        "top_skills": [{"skill": s, "count": c} for s, c in all_skills.most_common(10)],
        "avg_skills_per_posting": round(sum(len(p.get("required_skills", [])) for p in postings) / n, 2) if n else 0.0,
    }

def main():
    postings = load_extracted()
    kpi = compute_kpi(postings)
    print(json.dumps(kpi, indent=2))
    with open("docs/data/kpi.json", "w") as f:
        json.dump(kpi, f, indent=2)
    print("\nWrote docs/data/kpi.json")

if __name__ == "__main__":
    main()
