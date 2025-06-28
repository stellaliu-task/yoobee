from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_bloch_multivector, plot_histogram
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

# Create a quantum circuit with 3 qubits and 2 classical bits
qc = QuantumCircuit(3, 2)

# Step 1: Prepare the state to teleport (on qubit 0)
qc.h(0)             # Let's say we teleport |+⟩ = (|0⟩ + |1⟩)/√2
qc.barrier()

# Step 2: Create entanglement between qubits 1 and 2 (shared between Alice and Bob)
qc.h(1)
qc.cx(1, 2)
qc.barrier()

# Step 3: Alice applies CNOT and Hadamard
qc.cx(0, 1)
qc.h(0)
qc.barrier()

# Step 4: Alice measures and sends results (to Bob)
qc.measure(0, 0)
qc.measure(1, 1)
qc.barrier()

# Step 5: Bob applies corrections based on Alice's results
qc.x(2).c_if(qc.cregs[0], 1)  # If Alice's qubit 1 is 1, apply X
qc.z(2).c_if(qc.cregs[0], 2)  # If Alice's qubit 0 is 1, apply Z
qc.barrier()

# Draw the circuit
qc.draw('mpl')
