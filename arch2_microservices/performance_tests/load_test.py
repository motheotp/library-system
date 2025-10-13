"""
Load Testing Script for Library Management System
This script measures throughput and latency of the microservices architecture.
Run this from the project root: python tests/load_test.py
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime

API_URL = 'http://localhost:8080'

class LoadTestResults:
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.response_times = []
        self.errors = 0
        self.successes = 0
    
    def add_response(self, response_time):
        self.response_times.append(response_time)
        self.successes += 1
    
    def add_error(self):
        self.errors += 1
    
    def print_results(self):
        if self.response_times:
            avg_time = statistics.mean(self.response_times)
            min_time = min(self.response_times)
            max_time = max(self.response_times)
            p95 = statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else max_time
            throughput = self.successes / (sum(self.response_times) / 1000) if self.response_times else 0
            
            print(f"\n{'='*60}")
            print(f"Operation: {self.operation_name}")
            print(f"{'='*60}")
            print(f"Successful Requests:  {self.successes}")
            print(f"Failed Requests:      {self.errors}")
            print(f"Average Latency:      {avg_time:.2f}ms")
            print(f"Min Latency:          {min_time:.2f}ms")
            print(f"Max Latency:          {max_time:.2f}ms")
            print(f"P95 Latency:          {p95:.2f}ms")
            print(f"Throughput:           {throughput:.2f} req/s")
            print(f"{'='*60}")

def test_list_books(results):
    """Test listing all books"""
    try:
        start = time.time()
        response = requests.get(f'{API_URL}/books', timeout=10)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            results.add_response(elapsed)
        else:
            results.add_error()
    except Exception as e:
        results.add_error()

def run_load_test(num_workers=10, requests_per_worker=100, scenario_name="Test"):
    """
    Run load test with specified parameters
    
    Args:
        num_workers: Number of concurrent threads
        requests_per_worker: Requests per thread
        scenario_name: Name of the scenario for logging
    """
    print(f"\n{'#'*60}")
    print(f"# {scenario_name} Scenario")
    print(f"# Concurrent Workers: {num_workers}")
    print(f"# Requests per Worker: {requests_per_worker}")
    print(f"# Total Requests: {num_workers * requests_per_worker}")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    results = {
        'list_books': LoadTestResults('GET /books'),
    }
    
    total_start = time.time()
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        
        # List books requests
        for i in range(num_workers * requests_per_worker):
            futures.append(executor.submit(test_list_books, results['list_books']))
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            future.result()
    
    total_time = time.time() - total_start
    
    # Print results
    for operation, result in results.items():
        result.print_results()
    
    print(f"\nTotal Test Duration: {total_time:.2f} seconds")
    print(f"Scenario completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    """Run all load test scenarios"""
    print("\n" + "="*60)
    print("Library Management System - Load Testing Suite")
    print("="*60)
    
    # Scenario 1: Low Load
    run_load_test(num_workers=5, requests_per_worker=20, scenario_name="Low Load")
    input("Press Enter to continue to Medium Load test...")
    
    # Scenario 2: Medium Load
    run_load_test(num_workers=10, requests_per_worker=50, scenario_name="Medium Load")
    input("Press Enter to continue to High Load test...")
    
    # Scenario 3: High Load
    run_load_test(num_workers=25, requests_per_worker=100, scenario_name="High Load")
    
    print("\n" + "="*60)
    print("All load tests completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()