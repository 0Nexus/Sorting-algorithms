from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import copy

app = FastAPI(title="Sorting Algorithms API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SortRequest(BaseModel):
    array: List[int]
    algorithm: Optional[str] = None


class SortStep(BaseModel):
    array: List[int]
    comparing: List[int] = []
    swapping: List[int] = []
    sorted_indices: List[int] = []
    description: str = ""


class SortResponse(BaseModel):
    algorithm: str
    original: List[int]
    sorted: List[int]
    steps: List[SortStep]
    comparisons: int
    swaps: int
    time_complexity: str
    space_complexity: str
    stable: bool
    description: str


# ─── Algorithm Implementations ────────────────────────────────────────────────

def bubble_sort(arr):
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    sorted_set = set()

    for i in range(n):
        for j in range(n - i - 1):
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[j, j+1], sorted_indices=list(sorted_set),
                                   description=f"Comparing a[{j}]={a[j]} and a[{j+1}]={a[j+1]}"))
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                swaps += 1
                steps.append(SortStep(array=a[:], swapping=[j, j+1], sorted_indices=list(sorted_set),
                                       description=f"Swapping {a[j+1]} and {a[j]}"))
        sorted_set.add(n - i - 1)

    return steps, comparisons, swaps, a


def selection_sort(arr):
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    sorted_set = set()

    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[min_idx, j], sorted_indices=list(sorted_set),
                                   description=f"Comparing a[{min_idx}]={a[min_idx]} with a[{j}]={a[j]}"))
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            swaps += 1
            steps.append(SortStep(array=a[:], swapping=[i, min_idx], sorted_indices=list(sorted_set),
                                   description=f"Placing minimum {a[i]} at index {i}"))
        sorted_set.add(i)

    return steps, comparisons, swaps, a


def insertion_sort(arr):
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    sorted_set = set(range(1))

    for i in range(1, n):
        key = a[i]
        j = i - 1
        steps.append(SortStep(array=a[:], comparing=[i], sorted_indices=list(sorted_set),
                               description=f"Inserting element {key} into sorted portion"))
        while j >= 0 and a[j] > key:
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[j, j+1], sorted_indices=list(sorted_set),
                                   description=f"Shifting {a[j]} right"))
            a[j+1] = a[j]
            swaps += 1
            j -= 1
        if j >= 0:
            comparisons += 1
        a[j+1] = key
        sorted_set.add(i)
        steps.append(SortStep(array=a[:], swapping=[j+1], sorted_indices=list(sorted_set),
                               description=f"Placed {key} at position {j+1}"))

    return steps, comparisons, swaps, a


def merge_sort_helper(arr, steps, comparisons_ref, swaps_ref, left=0):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    L = merge_sort_helper(arr[:mid], steps, comparisons_ref, swaps_ref, left)
    R = merge_sort_helper(arr[mid:], steps, comparisons_ref, swaps_ref, left + mid)

    result = []
    i = j = 0
    while i < len(L) and j < len(R):
        comparisons_ref[0] += 1
        if L[i] <= R[j]:
            result.append(L[i]); i += 1
        else:
            result.append(R[j]); j += 1
        swaps_ref[0] += 1

    result.extend(L[i:])
    result.extend(R[j:])
    return result


def merge_sort(arr):
    steps = []
    a = arr[:]
    comparisons_ref = [0]
    swaps_ref = [0]

    def _merge_sort(sub, offset):
        if len(sub) <= 1:
            return sub
        mid = len(sub) // 2
        L = _merge_sort(sub[:mid], offset)
        R = _merge_sort(sub[mid:], offset + mid)

        merged = []
        i = j = 0
        while i < len(L) and j < len(R):
            comparisons_ref[0] += 1
            li, rj = offset + i, offset + mid + j
            steps.append(SortStep(
                array=a[:],
                comparing=[li, rj],
                description=f"Merging: comparing {L[i]} and {R[j]}"
            ))
            if L[i] <= R[j]:
                merged.append(L[i]); i += 1
            else:
                merged.append(R[j]); j += 1
            swaps_ref[0] += 1

        merged.extend(L[i:])
        merged.extend(R[j:])

        for k, val in enumerate(merged):
            a[offset + k] = val

        steps.append(SortStep(
            array=a[:],
            sorted_indices=list(range(offset, offset + len(merged))),
            description=f"Merged subarray at [{offset}:{offset+len(merged)}]"
        ))
        return merged

    _merge_sort(a, 0)
    return steps, comparisons_ref[0], swaps_ref[0], a


def quick_sort(arr):
    steps = []
    a = arr[:]
    comparisons_ref = [0]
    swaps_ref = [0]
    sorted_set = set()

    def _partition(lo, hi):
        pivot = a[hi]
        i = lo - 1
        steps.append(SortStep(array=a[:], comparing=[hi], sorted_indices=list(sorted_set),
                               description=f"Pivot = {pivot} at index {hi}"))
        for j in range(lo, hi):
            comparisons_ref[0] += 1
            steps.append(SortStep(array=a[:], comparing=[j, hi], sorted_indices=list(sorted_set),
                                   description=f"Comparing {a[j]} with pivot {pivot}"))
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
                swaps_ref[0] += 1
                steps.append(SortStep(array=a[:], swapping=[i, j], sorted_indices=list(sorted_set),
                                       description=f"Swapping {a[j]} and {a[i]}"))
        a[i+1], a[hi] = a[hi], a[i+1]
        swaps_ref[0] += 1
        sorted_set.add(i+1)
        steps.append(SortStep(array=a[:], swapping=[i+1, hi], sorted_indices=list(sorted_set),
                               description=f"Placing pivot {pivot} at position {i+1}"))
        return i + 1

    def _quick_sort(lo, hi):
        if lo < hi:
            p = _partition(lo, hi)
            _quick_sort(lo, p - 1)
            _quick_sort(p + 1, hi)

    _quick_sort(0, len(a) - 1)
    return steps, comparisons_ref[0], swaps_ref[0], a


def heap_sort(arr):
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    sorted_set = set()

    def heapify(n, i):
        nonlocal comparisons, swaps
        largest = i
        l, r = 2*i+1, 2*i+2
        if l < n:
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[largest, l], sorted_indices=list(sorted_set),
                                   description=f"Heapify: comparing a[{largest}]={a[largest]} with left child a[{l}]={a[l]}"))
            if a[l] > a[largest]:
                largest = l
        if r < n:
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[largest, r], sorted_indices=list(sorted_set),
                                   description=f"Heapify: comparing a[{largest}]={a[largest]} with right child a[{r}]={a[r]}"))
            if a[r] > a[largest]:
                largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            swaps += 1
            steps.append(SortStep(array=a[:], swapping=[i, largest], sorted_indices=list(sorted_set),
                                   description=f"Swapping {a[largest]} and {a[i]}"))
            heapify(n, largest)

    for i in range(n//2 - 1, -1, -1):
        heapify(n, i)

    for i in range(n-1, 0, -1):
        a[0], a[i] = a[i], a[0]
        swaps += 1
        sorted_set.add(i)
        steps.append(SortStep(array=a[:], swapping=[0, i], sorted_indices=list(sorted_set),
                               description=f"Placing max {a[i]} at position {i}"))
        heapify(i, 0)

    return steps, comparisons, swaps, a


def shell_sort(arr):
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    gap = n // 2

    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            steps.append(SortStep(array=a[:], comparing=[i],
                                   description=f"Shell sort gap={gap}: checking element {temp} at index {i}"))
            while j >= gap and a[j - gap] > temp:
                comparisons += 1
                steps.append(SortStep(array=a[:], comparing=[j, j-gap],
                                       description=f"Comparing a[{j}]={a[j]} with a[{j-gap}]={a[j-gap]}"))
                a[j] = a[j - gap]
                swaps += 1
                j -= gap
            if j >= gap:
                comparisons += 1
            a[j] = temp
        gap //= 2

    return steps, comparisons, swaps, a


def counting_sort(arr):
    steps = []
    a = arr[:]
    comparisons = 0
    swaps = 0

    if not a:
        return steps, 0, 0, a

    mn, mx = min(a), max(a)
    count = [0] * (mx - mn + 1)

    for val in a:
        count[val - mn] += 1
        steps.append(SortStep(array=a[:], comparing=[a.index(val)],
                               description=f"Counting {val}: count[{val}]={count[val-mn]}"))

    output = []
    for i, c in enumerate(count):
        output.extend([i + mn] * c)

    for i in range(len(a)):
        if a[i] != output[i]:
            swaps += 1
        a[i] = output[i]

    steps.append(SortStep(array=a[:], sorted_indices=list(range(len(a))),
                           description="Reconstructed sorted array from counts"))
    return steps, comparisons, swaps, a


def radix_sort(arr):
    steps = []
    a = arr[:]
    comparisons = 0
    swaps = 0

    if not a:
        return steps, 0, 0, a

    mx = max(a)
    exp = 1
    while mx // exp > 0:
        output = [0] * len(a)
        count = [0] * 10

        for val in a:
            digit = (val // exp) % 10
            count[digit] += 1

        steps.append(SortStep(array=a[:],
                               description=f"Radix pass for digit place {exp}: counting digits"))

        for i in range(1, 10):
            count[i] += count[i-1]

        for i in range(len(a)-1, -1, -1):
            digit = (a[i] // exp) % 10
            output[count[digit]-1] = a[i]
            count[digit] -= 1
            swaps += 1

        for i in range(len(a)):
            a[i] = output[i]

        steps.append(SortStep(array=a[:],
                               description=f"After radix pass exp={exp}: {a}"))
        exp *= 10

    return steps, comparisons, swaps, a


def bucket_sort(arr):
    steps = []
    a = arr[:]
    comparisons = swaps = 0

    if not a:
        return steps, 0, 0, a

    mn, mx = min(a), max(a)
    bucket_count = max(1, len(a) // 2)
    buckets = [[] for _ in range(bucket_count)]
    rng = mx - mn + 1

    for val in a:
        idx = min(int((val - mn) / rng * bucket_count), bucket_count - 1)
        buckets[idx].append(val)
        steps.append(SortStep(array=a[:],
                               description=f"Placing {val} into bucket {idx}"))

    sorted_arr = []
    for i, b in enumerate(buckets):
        b.sort()
        sorted_arr.extend(b)
        steps.append(SortStep(array=sorted_arr + a[len(sorted_arr):],
                               description=f"Sorted bucket {i}: {b}"))

    for i in range(len(a)):
        if a[i] != sorted_arr[i]:
            swaps += 1
        a[i] = sorted_arr[i]

    steps.append(SortStep(array=a[:], sorted_indices=list(range(len(a))),
                           description="All buckets merged"))
    return steps, comparisons, swaps, a


def cocktail_sort(arr):
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    sorted_set = set()
    swapped = True
    start, end = 0, n - 1

    while swapped:
        swapped = False
        for i in range(start, end):
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[i, i+1], sorted_indices=list(sorted_set),
                                   description=f"Forward pass: comparing a[{i}]={a[i]} and a[{i+1}]={a[i+1]}"))
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
                swaps += 1
                swapped = True
                steps.append(SortStep(array=a[:], swapping=[i, i+1], sorted_indices=list(sorted_set),
                                       description=f"Swapped {a[i+1]} and {a[i]}"))
        if not swapped:
            break
        sorted_set.add(end)
        end -= 1
        swapped = False
        for i in range(end-1, start-1, -1):
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[i, i+1], sorted_indices=list(sorted_set),
                                   description=f"Backward pass: comparing a[{i}]={a[i]} and a[{i+1}]={a[i+1]}"))
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
                swaps += 1
                swapped = True
                steps.append(SortStep(array=a[:], swapping=[i, i+1], sorted_indices=list(sorted_set),
                                       description=f"Swapped {a[i+1]} and {a[i]}"))
        sorted_set.add(start)
        start += 1

    return steps, comparisons, swaps, a


def gnome_sort(arr):
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    i = 0

    while i < n:
        if i == 0 or a[i] >= a[i-1]:
            comparisons += 1 if i > 0 else 0
            steps.append(SortStep(array=a[:], comparing=[max(0, i-1), i],
                                   description=f"Gnome at {i}: a[{i}]={a[i]} >= a[{i-1}]={a[i-1] if i > 0 else '?'}, move right"))
            i += 1
        else:
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[i-1, i],
                                   description=f"Gnome at {i}: a[{i}]={a[i]} < a[{i-1}]={a[i-1]}, swap and move left"))
            a[i], a[i-1] = a[i-1], a[i]
            swaps += 1
            i -= 1

    return steps, comparisons, swaps, a


def comb_sort(arr):
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    gap = n
    shrink = 1.3
    sorted_flag = False

    while not sorted_flag:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_flag = True

        for i in range(n - gap):
            comparisons += 1
            steps.append(SortStep(array=a[:], comparing=[i, i+gap],
                                   description=f"Comb gap={gap}: comparing a[{i}]={a[i]} and a[{i+gap}]={a[i+gap]}"))
            if a[i] > a[i+gap]:
                a[i], a[i+gap] = a[i+gap], a[i]
                swaps += 1
                sorted_flag = False
                steps.append(SortStep(array=a[:], swapping=[i, i+gap],
                                       description=f"Swapped {a[i+gap]} and {a[i]}"))

    return steps, comparisons, swaps, a


def tim_sort(arr):
    """Simplified TimSort illustration (insertion + merge)"""
    steps = []
    a = arr[:]
    n = len(a)
    comparisons = swaps = 0
    RUN = 8

    # Insertion sort runs
    for start in range(0, n, RUN):
        end = min(start + RUN - 1, n - 1)
        for i in range(start + 1, end + 1):
            temp = a[i]
            j = i - 1
            steps.append(SortStep(array=a[:], comparing=[i],
                                   description=f"TimSort insertion in run [{start}:{end+1}]: element {temp}"))
            while j >= start and a[j] > temp:
                comparisons += 1
                a[j+1] = a[j]
                swaps += 1
                j -= 1
            if j >= start:
                comparisons += 1
            a[j+1] = temp

    # Merge runs
    size = RUN
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                left_arr = a[left:mid+1]
                right_arr = a[mid+1:right+1]
                i = j = 0
                k = left
                while i < len(left_arr) and j < len(right_arr):
                    comparisons += 1
                    steps.append(SortStep(array=a[:], comparing=[left+i, mid+1+j],
                                           description=f"TimSort merge [{left}:{right+1}]: comparing {left_arr[i]} and {right_arr[j]}"))
                    if left_arr[i] <= right_arr[j]:
                        a[k] = left_arr[i]; i += 1
                    else:
                        a[k] = right_arr[j]; j += 1
                    swaps += 1; k += 1
                while i < len(left_arr):
                    a[k] = left_arr[i]; i += 1; k += 1
                while j < len(right_arr):
                    a[k] = right_arr[j]; j += 1; k += 1
                steps.append(SortStep(array=a[:], sorted_indices=list(range(left, right+1)),
                                       description=f"Merged run [{left}:{right+1}]"))
        size *= 2

    return steps, comparisons, swaps, a


# ─── Registry ─────────────────────────────────────────────────────────────────

ALGORITHMS = {
    "bubble":    (bubble_sort,    "O(n²)", "O(1)",    True,  "Repeatedly swaps adjacent elements if they're in the wrong order."),
    "selection": (selection_sort, "O(n²)", "O(1)",    False, "Finds the minimum and places it at the beginning each pass."),
    "insertion": (insertion_sort, "O(n²)", "O(1)",    True,  "Builds a sorted portion by inserting each element in its correct position."),
    "merge":     (merge_sort,     "O(n log n)", "O(n)", True, "Divides array in half, sorts each half recursively, then merges."),
    "quick":     (quick_sort,     "O(n log n) avg", "O(log n)", False, "Partitions array around a pivot, recursively sorts partitions."),
    "heap":      (heap_sort,      "O(n log n)", "O(1)", False, "Builds a max-heap then extracts elements one by one."),
    "shell":     (shell_sort,     "O(n log² n)", "O(1)", False, "Generalization of insertion sort with reducing gap sequences."),
    "counting":  (counting_sort,  "O(n+k)", "O(k)",  True,  "Counts occurrences of each value, then reconstructs the sorted array."),
    "radix":     (radix_sort,     "O(nk)",  "O(n+k)", True,  "Sorts by individual digits from least to most significant."),
    "bucket":    (bucket_sort,    "O(n+k)", "O(n)",   True,  "Distributes elements into buckets, sorts each bucket individually."),
    "cocktail":  (cocktail_sort,  "O(n²)", "O(1)",    True,  "Bidirectional bubble sort — passes alternate forward and backward."),
    "gnome":     (gnome_sort,     "O(n²)", "O(1)",    True,  "Like insertion sort but moves backward to fix order, then forward."),
    "comb":      (comb_sort,      "O(n log n)", "O(1)", False, "Improvement over bubble sort using a reducing gap between compared elements."),
    "tim":       (tim_sort,       "O(n log n)", "O(n)", True, "Hybrid of merge sort and insertion sort, used in Python & Java."),
}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Sorting Algorithms API", "algorithms": list(ALGORITHMS.keys())}


@app.get("/algorithms")
def list_algorithms():
    return {
        "algorithms": [
            {
                "id": k,
                "name": k.capitalize() + " Sort",
                "time_complexity": v[1],
                "space_complexity": v[2],
                "stable": v[3],
                "description": v[4],
            }
            for k, v in ALGORITHMS.items()
        ]
    }


@app.post("/sort/{algorithm}", response_model=SortResponse)
def sort(algorithm: str, req: SortRequest):
    algorithm = algorithm.lower()
    if algorithm not in ALGORITHMS:
        raise HTTPException(404, f"Algorithm '{algorithm}' not found. Available: {list(ALGORITHMS.keys())}")

    fn, time_c, space_c, stable, desc = ALGORITHMS[algorithm]
    steps, comparisons, swaps, sorted_arr = fn(req.array)

    return SortResponse(
        algorithm=algorithm,
        original=req.array,
        sorted=sorted_arr,
        steps=steps,
        comparisons=comparisons,
        swaps=swaps,
        time_complexity=time_c,
        space_complexity=space_c,
        stable=stable,
        description=desc,
    )


@app.post("/sort", response_model=List[SortResponse])
def sort_all(req: SortRequest):
    results = []
    for algo_id in ALGORITHMS:
        fn, time_c, space_c, stable, desc = ALGORITHMS[algo_id]
        steps, comparisons, swaps, sorted_arr = fn(req.array[:])
        results.append(SortResponse(
            algorithm=algo_id,
            original=req.array,
            sorted=sorted_arr,
            steps=steps,
            comparisons=comparisons,
            swaps=swaps,
            time_complexity=time_c,
            space_complexity=space_c,
            stable=stable,
            description=desc,
        ))
    return results
