from dotenv import load_dotenv
import os
from qiskit import (
    Aer,
    IBMQ,
    QuantumRegister,
    ClassicalRegister,
    QuantumCircuit,
    execute,
)
from qiskit.providers.ibmq import least_busy
from pymongo import MongoClient
from tqdm import tqdm

load_dotenv()

MOCK_BACKEND = os.getenv("MOCK_BACKEND") == "true"
DB_URL = os.getenv("DB_URL")
IBM_API_KEY = os.getenv("IBM_API_KEY")

NUM_SHOTS = 20000

db = MongoClient(DB_URL).db
available_results = db.flips.count_documents({"hasBeenUsed": False})
if available_results > 5000:
    print("{} results present, not running".format(available_results))
    quit()

if MOCK_BACKEND:
    backend = Aer.get_backend("aer_simulator")
else:
    IBMQ.save_account(IBM_API_KEY)
    IBMQ.load_account()  # Load account from disk
    providers = IBMQ.providers()  # List all available providers
    provider = providers[0]

    small_devices = provider.backends(
        filters=lambda x: x.configuration().n_qubits == 5
        and not x.configuration().simulator
    )
    backend = least_busy(small_devices)


# measure a single qubit after a hadamard gate
qr = QuantumRegister(1)
cr = ClassicalRegister(1)
circuit = QuantumCircuit(qr, cr)
circuit.h(qr[0])
circuit.measure(qr, cr)

job = execute(circuit, backend, shots=NUM_SHOTS, memory=True)
print("Waiting for job to finish...")
job.wait_for_final_state()

data = job.result().get_memory()

for i in tqdm(range(int(NUM_SHOTS / 1000))):
    db.flips.insert_many(
        [
            {"job_id": job.job_id(), "result": int(result), "hasBeenUsed": False}
            for result in data[i * 1000 : (i + 1) * 1000]
        ]
    )

db.flips.delete_many({"hasBeenUsed": True})
