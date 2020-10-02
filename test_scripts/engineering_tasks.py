from typing import List
from pathlib import Path


def prepare_simulation_data(base_file: str, parameters: List[dict]):
    file_names = []
    for i in range(len(parameters)):
        file_name = f"sim_inp_file_{i}.inp"
        with open(file_name, "w") as f:
            f.write("sim data")
        file_names.append(file_name)
    return file_names


def run_simulation(inp_file: str):
    p = Path(inp_file)
    out_file_name = p.stem + ".res"
    with open(out_file_name, "w") as f:
        f.write("sim data")


def post_process_simulation_data(res_files: List[str]) -> dict:
    with open("report.pdf", "wb") as f:
        f.write(b"sim data")
    output = {"number_of_simulation": len(res_files)}
    return output
