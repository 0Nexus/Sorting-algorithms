# SORT — Sorting Algorithm Visualizer

A FastAPI backend + visual frontend showcasing **14 sorting algorithms** with step-by-step visualization.

## Algorithms Included

| Algorithm     | Time Complexity  | Space | Stable |
|---------------|-----------------|-------|--------|
| Bubble Sort   | O(n²)           | O(1)  | ✓      |
| Selection Sort| O(n²)           | O(1)  | ✗      |
| Insertion Sort| O(n²)           | O(1)  | ✓      |
| Merge Sort    | O(n log n)      | O(n)  | ✓      |
| Quick Sort    | O(n log n) avg  | O(log n)| ✗    |
| Heap Sort     | O(n log n)      | O(1)  | ✗      |
| Shell Sort    | O(n log² n)     | O(1)  | ✗      |
| Counting Sort | O(n+k)          | O(k)  | ✓      |
| Radix Sort    | O(nk)           | O(n+k)| ✓      |
| Bucket Sort   | O(n+k)          | O(n)  | ✓      |
| Cocktail Sort | O(n²)           | O(1)  | ✓      |
| Gnome Sort    | O(n²)           | O(1)  | ✓      |
| Comb Sort     | O(n log n)      | O(1)  | ✗      |
| Tim Sort      | O(n log n)      | O(n)  | ✓      |

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API server
```bash
uvicorn main:app --reload --port 8000
```

### 3. Open the frontend
Open `index.html` in your browser (or serve it):
```bash
python -m http.server 3000
# then visit http://localhost:3000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET  | `/` | Root info |
| GET  | `/algorithms` | List all algorithms with metadata |
| POST | `/sort/{algorithm}` | Sort with step-by-step data |
| POST | `/sort` | Run all algorithms on same input |

### Example Request
```bash
curl -X POST http://localhost:8000/sort/bubble \
  -H "Content-Type: application/json" \
  -d '{"array": [64, 34, 25, 12, 22, 11, 90]}'
```

### Example Response
```json
{
  "algorithm": "bubble",
  "original": [64, 34, 25, 12, 22, 11, 90],
  "sorted": [11, 12, 22, 25, 34, 64, 90],
  "steps": [
    {
      "array": [64, 34, 25, 12, 22, 11, 90],
      "comparing": [0, 1],
      "swapping": [],
      "sorted_indices": [],
      "description": "Comparing a[0]=64 and a[1]=34"
    },
    ...
  ],
  "comparisons": 21,
  "swaps": 15,
  "time_complexity": "O(n²)",
  "space_complexity": "O(1)",
  "stable": true,
  "description": "Repeatedly swaps adjacent elements..."
}
```

## Features
- **Step-by-step visualization** — see every comparison and swap
- **Color coding** — yellow=comparing, red=swapping, green=sorted
- **Speed control** — adjustable via array size slider
- **Manual stepping** — go one step at a time
- **Stats** — live comparison/swap counters
- **Fallback mode** — frontend works offline with client-side bubble sort demo
>>>>>>> master
