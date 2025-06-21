import cirq
import numpy as np
from collections import Counter
import itertools

# Define the 2-bit function f with period 10
def f(x):
    lookup = {
        0b00: 0b01,
        0b01: 0b10,
        0b10: 0b01,
        0b11: 0b10
    }
    return lookup[x]

# Build the 16x16 oracle matrix: |x>|y> → |x>|y ⊕ f(x)>
oracle_matrix = np.zeros((16, 16), dtype=float)

for x, y in itertools.product(range(4), range(4)):
    input_index = (x << 2) | y
    output_index = (x << 2) | (y ^ f(x))
    oracle_matrix[output_index][input_index] = 1

# Convert the matrix to a Cirq gate
oracle_gate = cirq.MatrixGate(oracle_matrix)

# Define Simon's circuit
def simon_circuit(oracle_gate):
    qubits = cirq.LineQubit.range(4)
    circuit = cirq.Circuit()

    # Apply Hadamard to first two qubits (x register)
    circuit.append(cirq.H.on_each(qubits[0], qubits[1]))

    # Apply oracle gate to all 4 qubits
    circuit.append(oracle_gate(*qubits))

    # Apply Hadamard again to first two qubits
    circuit.append(cirq.H.on_each(qubits[0], qubits[1]))

    # Measure first two qubits
    circuit.append([cirq.measure(qubits[i], key=f'result_{i}') for i in range(2)])

    return circuit

# Main
if __name__ == "__main__":
    circuit = simon_circuit(oracle_gate)
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=100)

    # Collect and display results
    measurements = result.measurements
    counts = Counter(tuple(measurements[f'result_{i}'][j][0] for i in range(2)) for j in range(100))

    print("Measurement results (bitstring: frequency):")
    for outcome, frequency in counts.items():
        print(f"{outcome}: {frequency}")

    print("\nQuantum circuit:")
    print(circuit)
