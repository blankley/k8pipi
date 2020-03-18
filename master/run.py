import argparse
import json
import os
import time
import sys
import redis
import random
from kubernetes import client, config
import urllib3

urllib3.disable_warnings()

def random_seeds(chunks):
    return random.sample( range(10000,99999), chunks )

api_key= os.getenv("API_KEY") 
if not api_key:
    print("No API set in env variables")
    sys.exit(1)

kube_host= os.getenv("KUBE_HOST","https://kubernetes.default")
redis_host = os.getenv("REDIS_HOST","redis.default")
sim_name = os.getenv("SIM_NAME","pi_sim")
namespace = os.getenv("SIM_NAMESPACE","pi")
config_file = os.getenv("CONFIG_FILE","pi_sim_config10.json")

if config_file == "custom":
    chunks = int(os.getenv("SIM_CHUNKS", 100))
    iterations = int(os.getenv("SIM_ITERATIONS", 10000000))
    seeds = random_seeds(chunks)
else:
    with open(f"configs/{config_file}",'r') as json_file:
        sim_config = json.load(json_file)
        iterations = int(sim_config["iterations_per_chunk"])
        try:
            seeds = sim_config['seeds']
        except:
            seeds = random_seeds(sim_config['chunks'])

configuration = client.Configuration()
configuration.host = kube_host
configuration.verify_ssl=False
configuration.api_key['authorization'] = api_key
configuration.api_key_prefix['authorization'] = 'Bearer'
api = client.BatchV1Api(client.ApiClient(configuration))

with open('job.json','r') as job_file:
    job = json.load(job_file)
jobs = []

print("Starting jobs")

for seed in seeds:
   myjob = job
   name = f"calculate-pi-{seed}"
   myjob['metadata']['name'] = name
   myjob['spec']['template']['spec']['containers'][0]['command'][1] = sim_name
   myjob['spec']['template']['spec']['containers'][0]['command'][2] = f"{seed}"
   myjob['spec']['template']['spec']['containers'][0]['command'][3] = f"{iterations}"
   myjob['spec']['template']['spec']['containers'][0]['command'][4] = redis_host
   resp = api.create_namespaced_job(namespace,myjob)
   print(f"Start job: {name}")
   jobs.append(name)

print("Waiting for jobs to finish")

succeeded = False

while not succeeded:
  succeeded = True
  for job in jobs:
    status = api.read_namespaced_job_status(job,namespace);
    if not status.status.succeeded:
        succeeded = False
  print("Waiting...")
  time.sleep(30)

print("Done. Cleaning up jobs")

for job in jobs:
   print(f"deleted job {job}")
   del_job = api.delete_namespaced_job(job, namespace,propagation_policy='Background')


print("Calculating Pi:")

r = redis.Redis(host=redis_host, port=6379, db=0)
aHits = []

while 1:
  pop = r.lpop(sim_name)
  if pop == None:
      break
  aHits.append(pop)

total_hits = 0
total_iterations = 0

for hits in aHits:
  total_hits = total_hits + int(hits)
  total_iterations = total_iterations + iterations

pi = 4/(total_iterations/total_hits)

print(pi)
