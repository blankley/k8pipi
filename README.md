# Calculate Pi with distributed kubernetes jobs.

> Based on [FredHutch/batch-pi](https://github.com/FredHutch/batch-pi)

Calculate the value of PI using the Monte Carlo simulation.

# Quick Start

- Deploy redis to the default namespace

`kubectl create deploy redis --image=redis`
`kubectl expose deploy redis --port=6379 --target-port=6379`

- create a namespace pi

`kubectl create namespace pi`

- Set the API_KEY env variable in the pi-master.yaml (Look in your ~/.kube/config file user: token:)

- Deploy the master job

`kubectl apply -f pi-master.yaml`

- Wait until all the jobs complete

`kubectl -n pi get jobs`

- Read the value for Pi:

`kubectl -n pi logs -l job-name=calculate-pi-master`
