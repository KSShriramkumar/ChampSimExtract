from champsimextract.core import BaseMetric, BaselinedMetric, CustomMetric
IPC = BaseMetric(
    name="IPC",
    regex_pattern=r"CPU \d+ cumulative IPC:\s+([0-9]*\.[0-9]+).*"
)
INSTRUCTION_COUNT = BaseMetric(
    name="Instruction Count",
    regex_pattern=r"Simulation\s+Instructions:\s+([0-9]+)"
)
def get_miss_metric(cache:str,type:str) -> BaseMetric:
    '''Generates a BaseMetric to extract the number of misses for a given cache and access type.'''
    pattern = rf"{cache}\s+{type}\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+)"
    name = f"{cache}_{type}_MISSES"
    return BaseMetric(
        name=name,
        regex_pattern=pattern
    )
def get_mpki_metric(cache:str,type:str) -> CustomMetric:
    '''Generates a BaseMetric to extract the MPKI for a given cache and access type.'''
    name = f"{cache}_{type}_MPKI"
    return CustomMetric(
        name=name,
        metrics=[get_miss_metric(cache,type), INSTRUCTION_COUNT],
        process_func=lambda misses, instructions: (misses / instructions) *1000
    ) 

LLC_RFO_MISSES = get_miss_metric("LLC", "RFO")
LLC_LOAD_MISSES = get_miss_metric("LLC", "LOAD")
LLC_TOTAL_MISSES = get_miss_metric("LLC", "TOTAL")

LLC_RFO_MPKI = get_mpki_metric("LLC", "RFO")
LLC_LOAD_MPKI = get_mpki_metric("LLC", "LOAD")  
LLC_TOTAL_MPKI = get_mpki_metric("LLC", "TOTAL")

LLC_SLICE_RFO_MISSES = lambda x: get_miss_metric(f"LLC_slice_{x}","RFO")
LLC_SLICE_LOAD_MISSES = lambda x: get_miss_metric(f"LLC_slice_{x}","LOAD")
LLC_SLICE_TOTAL_MISSES = lambda x: get_miss_metric(f"LLC_slice_{x}","TOTAL")


LLC_SLICE_RFO_MPKI = lambda x: get_mpki_metric(f"LLC_slice_{x}","RFO")
LLC_SLICE_LOAD_MPKI = lambda x: get_mpki_metric(f"LLC_slice_{x}","LOAD")
LLC_SLICE_TOTAL_MPKI = lambda x: get_mpki_metric(f"LLC_slice_{x}","TOTAL")
