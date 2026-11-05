import time
import random
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Dual Sorting Telemetry Engine",
    description="Heap Sort & Counting Sort Step-by-Step Visualization API",
    version="1.0.0"
)

# Enable CORS for Google Apps Script and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SortRequest(BaseModel):
    array: Optional[List[int]] = Field(default=None, description="Custom array to sort")
    size: int = Field(default=24, ge=8, le=64, description="Array size if array is not provided")
    min_val: int = Field(default=10, ge=1, le=500, description="Minimum value")
    max_val: int = Field(default=99, ge=2, le=500, description="Maximum value")


def generate_heap_sort_steps(arr: List[int]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    a = arr.copy()
    n = len(a)
    steps = []
    comparisons = 0
    swaps = 0
    start_time = time.perf_counter()

    steps.append({
        "step": 0,
        "phase": "INIT",
        "description": f"초기 상태 (N={n})",
        "array": a.copy(),
        "active_indices": [],
        "heap_size": n,
        "comparisons": comparisons,
        "swaps": swaps,
        "progress": 0.0,
        "complexity_metric": 0
    })

    def heapify(size: int, root: int):
        nonlocal comparisons, swaps
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < size:
            comparisons += 1
            if a[left] > a[largest]:
                largest = left

        if right < size:
            comparisons += 1
            if a[right] > a[largest]:
                largest = right

        if largest != root:
            a[root], a[largest] = a[largest], a[root]
            swaps += 1
            steps.append({
                "step": len(steps),
                "phase": "HEAPIFY",
                "description": f"Sift Down: index {root}({a[largest]}) ⇄ index {largest}({a[root]})",
                "array": a.copy(),
                "active_indices": [root, largest],
                "heap_size": size,
                "comparisons": comparisons,
                "swaps": swaps,
                "complexity_metric": comparisons + swaps
            })
            heapify(size, largest)

    # 1. Build Max Heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)
        steps.append({
            "step": len(steps),
            "phase": "BUILD_HEAP",
            "description": f"최대 힙 구성: 서브트리 루트 index {i} 힙화",
            "array": a.copy(),
            "active_indices": [i],
            "heap_size": n,
            "comparisons": comparisons,
            "swaps": swaps,
            "complexity_metric": comparisons + swaps
        })

    # 2. Extract elements from heap one by one
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        swaps += 1
        steps.append({
            "step": len(steps),
            "phase": "EXTRACT_MAX",
            "description": f"최댓값(루트 {a[i]})을 정렬 위치 index {i}로 이동",
            "array": a.copy(),
            "active_indices": [0, i],
            "heap_size": i,
            "comparisons": comparisons,
            "swaps": swaps,
            "complexity_metric": comparisons + swaps
        })
        heapify(i, 0)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    steps.append({
        "step": len(steps),
        "phase": "COMPLETED",
        "description": "힙 정렬 완료",
        "array": a.copy(),
        "active_indices": [],
        "heap_size": 0,
        "comparisons": comparisons,
        "swaps": swaps,
        "complexity_metric": comparisons + swaps
    })

    total_steps = max(1, len(steps) - 1)
    for idx, s in enumerate(steps):
        s["progress"] = round((idx / total_steps) * 100, 1)

    metadata = {
        "total_steps": len(steps),
        "comparisons": comparisons,
        "swaps": swaps,
        "operations": comparisons + swaps,
        "elapsed_ms": round(elapsed_ms, 3),
        "time_complexity": "O(N log N)",
        "space_complexity": "O(1) [In-place]"
    }
    return steps, metadata


def generate_counting_sort_steps(arr: List[int]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    a = arr.copy()
    n = len(a)
    steps = []
    passes = 0
    start_time = time.perf_counter()

    min_val = min(a) if a else 0
    max_val = max(a) if a else 0
    k = max_val - min_val + 1

    count = [0] * k
    output = [0] * n

    steps.append({
        "step": 0,
        "phase": "INIT",
        "description": f"카운팅 테이블 초기화 (범위 {min_val}~{max_val}, K={k})",
        "array": output.copy(),
        "active_indices": [],
        "count_table": {idx + min_val: 0 for idx in range(min(k, 10))},
        "passes": 0,
        "comparisons": 0,
        "complexity_metric": 0
    })

    # 1. Frequency Count
    for i in range(n):
        val = a[i]
        count[val - min_val] += 1
        passes += 1
        steps.append({
            "step": len(steps),
            "phase": "COUNT_FREQUENCY",
            "description": f"빈도수 집계: 값 {val} 카운트 → {count[val - min_val]}회",
            "array": output.copy(),
            "active_indices": [i],
            "current_val": val,
            "count_table": {idx + min_val: count[idx] for idx in range(min(k, 10))},
            "passes": passes,
            "comparisons": 0,
            "complexity_metric": passes
        })

    # 2. Prefix Sums (Cumulative count)
    for i in range(1, k):
        count[i] += count[i - 1]
        passes += 1
        if i % max(1, k // 4) == 0 or i == k - 1:
            steps.append({
                "step": len(steps),
                "phase": "PREFIX_SUM",
                "description": f"누적 도수 갱신: 값 {i + min_val}의 누적 위치 = {count[i]}",
                "array": output.copy(),
                "active_indices": [],
                "count_table": {idx + min_val: count[idx] for idx in range(min(k, 10))},
                "passes": passes,
                "comparisons": 0,
                "complexity_metric": passes
            })

    # 3. Placement in output array (stable backwards scan)
    for i in range(n - 1, -1, -1):
        val = a[i]
        pos = count[val - min_val] - 1
        output[pos] = val
        count[val - min_val] -= 1
        passes += 1
        steps.append({
            "step": len(steps),
            "phase": "BUILD_OUTPUT",
            "description": f"배치: 값 {val}을 정렬 배열 index {pos}에 저장",
            "array": output.copy(),
            "active_indices": [pos],
            "current_val": val,
            "count_table": {idx + min_val: count[idx] for idx in range(min(k, 10))},
            "passes": passes,
            "comparisons": 0,
            "complexity_metric": passes
        })

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    steps.append({
        "step": len(steps),
        "phase": "COMPLETED",
        "description": "도수 정렬 완료 (비교 연산 0회)",
        "array": output.copy(),
        "active_indices": [],
        "count_table": {idx + min_val: count[idx] for idx in range(min(k, 10))},
        "passes": passes,
        "comparisons": 0,
        "complexity_metric": passes
    })

    total_steps = max(1, len(steps) - 1)
    for idx, s in enumerate(steps):
        s["progress"] = round((idx / total_steps) * 100, 1)

    metadata = {
        "total_steps": len(steps),
        "comparisons": 0,
        "total_passes": passes,
        "operations": passes,
        "elapsed_ms": round(elapsed_ms, 3),
        "time_complexity": "O(N + K)",
        "space_complexity": f"O(K) [Auxiliary Table K={k}]"
    }
    return steps, metadata


@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "service": "Dual Sorting Telemetry API",
        "engine": "FastAPI",
        "timestamp": time.time()
    }


@app.post("/api/sort")
def sort_endpoint(req: SortRequest):
    if req.array:
        initial_array = req.array
    else:
        min_v = min(req.min_val, req.max_val)
        max_v = max(req.min_val, req.max_val)
        initial_array = [random.randint(min_v, max_v) for _ in range(req.size)]

    heap_steps, heap_meta = generate_heap_sort_steps(initial_array)
    counting_steps, counting_meta = generate_counting_sort_steps(initial_array)

    return {
        "status": "success",
        "initial_array": initial_array,
        "size": len(initial_array),
        "min_value": min(initial_array),
        "max_value": max(initial_array),
        "heap_sort": {
            "metadata": heap_meta,
            "steps": heap_steps
        },
        "counting_sort": {
            "metadata": counting_meta,
            "steps": counting_steps
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

