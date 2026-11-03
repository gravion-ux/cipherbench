from statistics import median


def summarize(records: list[dict]):
    grouped={}
    for row in records:
        name=row.get("algorithm")
        elapsed=row.get("elapsed_ms")
        if not isinstance(name,str) or not isinstance(elapsed,(int,float)) or elapsed < 0:
            continue
        grouped.setdefault(name,[]).append(float(elapsed))
    return [{"algorithm":name,"samples":len(values),"median_ms":median(values),
             "min_ms":min(values),"max_ms":max(values)}
            for name,values in sorted(grouped.items())]
