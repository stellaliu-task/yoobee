from qiskit import QuantumCircuit, BasicAer, execute

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

backend = BasicAer.get_backend('qasm_simulator')
result = execute(qc, backend, shots=1024).result()
counts = result.get_counts()

print(counts)
