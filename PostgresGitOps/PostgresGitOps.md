# Day 2 Operations for PostgreSQL Clusters on Kubernetes at Scale

It is critical that Postgres clusters are optimized, updated regularly and have routine maintenance to ensure that the environment stays stable, secure and performant.  The process of achieving this is often referred to as Day 2 operations.  Performing Day 2 operations can be complex and time consuming; especially if you are supporting a large number Postgres clusters.

To date, infrastructure management has mostly been a manual process.  However, with the adoption of [Gitops](https://about.gitlab.com/topics/gitops/) and a little help from a continuos delivery tool like [Argo CD](https://argo-cd.readthedocs.io/en/stable/) you can reduce the complexity and even automate your Day 2 operations. The declarative nature of Crunchy Postgres for Kubernetes (CPK) makes it a perfect candidate for gitops. Let's take a look at how gitops and Argo CD can help perform Day 2 Operations on your Crunchy Data Postgres cluster on kubernetes.

## The "Git" in Gitops

In order to perform gitops operations you must check-in your infrastructure files to Git.  Im my github repo I have a file structure that separates the files into admin, base and overlay directories. This structure helps isolate files so they can be independently run via [Kustomize](https://kustomize.io/) in Argo CD.

- PostgresGitOps:
  - gitops:
    - admin:
      - reset-password:
        <details>
          <summary>- kustomization.yaml</summary>

        ``` yaml
        resources:
        - resetpassword.yaml
        ```
        </details>

        <details><summary>- resetpassword.yaml</summary>

        ``` yaml
        apiVersion: v1
        data:
          password: 
        kind: Secret
        metadata:
          name: <cluster_name>-pguser-<cluster_name>
        type: Opaque
        ```

        </details>
      - shutdown:
        <details><summary>- kustomization.yaml</summary>

        ``` yaml
        bases:
          - ../../base/postgres
        
        patchesStrategicMerge:
          - postgres.yaml
        ```
        
        </details>
        <details><summary>- postgres.yaml</summary>
        
        ``` yaml
        apiVersion: postgres-operator.crunchydata.com/v1beta1
        kind: PostgresCluster
        metadata:
          name: <cluster_name>
        spec:
          shutdown: true
        ```
        
        </details>
      - startup:
        <details><summary>- kustomization.yaml</summary>

        ``` yaml
        bases:
          - ../../base/postgres
        
        patchesStrategicMerge:
          - postgres.yaml
        ```
        
        </details>
        <details><summary>- postgres.yaml</summary>

        ``` yaml
        apiVersion: postgres-operator.crunchydata.com/v1beta1
        kind: PostgresCluster
        metadata:
          name: <cluster_name>
        spec:
          shutdown: false
        ```
        
        </details>
    - base:
      - postgres:
        <details><summary>- kustomization.yaml</summary>

        ``` yaml
        resources:
        - postgres.yaml
        ```
        
        </details>
        <details><summary>- postgres.yaml</summary>

        ``` yaml
        apiVersion: postgres-operator.crunchydata.com/v1beta1
        kind: PostgresCluster
        metadata:
          name: <cluster_name>
        spec:
          users:
            - name: <cluster_name>
              databases:
                 - <cluster_name>db
          image: registry.developers.crunchydata.com/crunchydata/crunchy-postgres:ubi8-14.5-1
          postgresVersion: 14
          shutdown: false
          port: 5432
          instances:
            - name: 'pgdb'
              replicas: 1
              resources:
                limits:
                  cpu: 1.0
                  memory: 1Gi
              dataVolumeClaimSpec:
                accessModes:
                - "ReadWriteOnce"
                resources:
                  requests:
                    storage: 1Gi

          backups:
            pgbackrest:
              image: registry.developers.crunchydata.com/crunchydata/crunchy-pgbackrest:ubi8-2.40-1
              repos:
              - name: repo1
                volume:
                  volumeClaimSpec:
                    accessModes:
                    - "ReadWriteOnce"
                    resources:
                      requests:
                        storage: 1Gi

          patroni:
            dynamicConfiguration:
              postgresql:
                parameters:
                  max_parallel_workers: 2
                  max_worker_processes: 2
                  shared_buffers: 256MB
                  work_mem: 5MB
                  archive_timeout: 600
        ```
        
        </details>
    - overlays:
      - dev:
        <details><summary>- kustomization.yaml</summary>

        ``` yaml
        bases:
          - ../../base/postgres
        
        patchesStrategicMerge:
          - postgres.yaml
        ```
        
        </details>
        <details><summary>- postgres.yaml</summary>

        ``` yaml
        apiVersion: postgres-operator.crunchydata.com/v1beta1
        kind: PostgresCluster
        metadata:
          name: <cluster_name>
        spec:
          postgresVersion: 14
        ```
        
        </details>
      - prod:
        <details><summary>- kustomization.yaml</summary>

        ``` yaml
        bases:
          - ../../base/postgres
        
        patchesStrategicMerge:
          - postgres.yaml
        ```
        
        </details>
        <details><summary>- postgres.yaml</summary>

        ``` yaml
        apiVersion: postgres-operator.crunchydata.com/v1beta1
        kind: PostgresCluster
        metadata:
          name: <cluster_name>
        spec:
          postgresVersion: 14
          instances:
            - name: 'pgdb'
              replicas: 2
              resources:
                limits:
                  cpu: 1.0
                  memory: 1Gi
              dataVolumeClaimSpec:
                accessModes:
                - "ReadWriteOnce"
                resources:
                  requests:
                    storage: 5Gi

          backups:
            pgbackrest:
              repos:
              - name: repo1
                schedules:
                  full: "0 1 * * 0"
                  incremental: "0 1 * * 1-6"
                volume:
                  volumeClaimSpec:
                    accessModes:
                    - "ReadWriteOnce"
                    resources:
                      requests:
                        storage: 1Gi

          monitoring:
            pgmonitor:
              exporter:
                image: registry.developers.crunchydata.com/crunchydata/crunchy-postgres-exporter:ubi8-5.2.1-0

          patroni:
            dynamicConfiguration:
              postgresql:
                parameters:
                  max_parallel_workers: 2
                  max_worker_processes: 2
                  shared_buffers: 512MB
                  archive_timeout: 600
        ```
        
        </details>
      - qa:
        <details><summary>- kustomization.yaml</summary>

        ``` yaml
        bases:
          - ../../base/postgres
        
        patchesStrategicMerge:
          - postgres.yaml
        ```
        
        </details>
        <details><summary>- postgres.yaml</summary>

        ``` yaml
        apiVersion: postgres-operator.crunchydata.com/v1beta1
        kind: PostgresCluster
        metadata:
          name: <cluster_name>
        spec:
          postgresVersion: 14

          backups:
            pgbackrest:
              repos:
              - name: repo1
                schedules:
                  full: "0 1 * * 0"
                volume:
                  volumeClaimSpec:
                    accessModes:
                    - "ReadWriteOnce"
                    resources:
                      requests:
                        storage: 1Gi

          monitoring:
            pgmonitor:
              exporter:
                image: registry.developers.crunchydata.com/crunchydata/crunchy-postgres-exporter:ubi8-5.2.1-0
        ```
        
        </details>



In gitops, Git is used as the [Single Source of Truth](https://en.wikipedia.org/wiki/Single_source_of_truth) to manage all infrastructure files.  The files used in the preceding examples manage artifacts to deploy the Postgres clusters and perform declarative Day 2 Operations on them. You can copy and paste the example files into your own files and check them in to your git repo.</br>

***Note:*** Ensure that you replace the ```<cluster_name>``` place holder with your own cluster name and use the same value in all of the example files.

## Argo CD

Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes.  It provides a UI and CLI that makes it easy to deploy and manage your applications running on Kubernetes. To install Argo CD in your kubernetes cluster simply run the following:

``` bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Additional details can be found in their [getting started guide](https://argo-cd.readthedocs.io/en/stable/getting_started/).

To access the Argo CD UI I have changed the argocd-sever service from ClusterIP to LoadBalancer.  This provides and external IP that I can access from my browser.  You could also use a port forward or an ingress.

``` bash
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

Once you have launched the Argo CD UI you can login.  The initial password for the ***admin*** account can be retrieved from the argocd-initial-admin-secret.

``` bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

### Configuring ARGO CD
Now that you have logged in you are ready to start configuring Argo CD to deploy and manage your Postgres cluster on Kubernetes.  The Argo CD UI should look like this:
![](pics/app-screen.png)
#### Add the Git Repository
You need to add your git repository to Argo CD.  Click on 'Settings' in the navigation bar on the left.

![](pics/settings.png)
Now click on 'Repositories' and the 'Connect Repo' buttons.  Provide the necessary information and click 'Save'.  Your should now have a connected repo.  If not, please review your settings and try again.
![](pics/connect-repo.png) 
#### Create the Projects
Argo CD uses projects to logically group applications.  I created three projects:
* deploy
* reset-password
* start-stop
  
![](pics/project-list.png)
To create a project click on 'Settings' in the navigation bar on the left.  Click on 'Project' and then the 'New Project' button.  Provide a project name and description in the panel on the right and click create.
Add your repo to 'Source Repositories' and add your Kubernetes cluster to 'Destinations' as seen here:
![](pics/deploy-project.png)
***Note:*** For this blog I deployed Argo CD in the same Kubernetes cluster that I am deploying Postgres into.  Please refer to the [Argo CD Documentation](https://argo-cd.readthedocs.io/en/stable/) for other deployment options.

Repeat the steps for each project you want to create.

### Creating Applications
Argo CD uses applications to perform declarative operations on its configured Kubernetes cluster. We will create several applications to deploy Postgres clusters and perform day 2 operations across 3 namespaces.

***Operations***
* deploy-postgres
* start-postgres
* stop-postgres
* reset-password

Create the namespaces in the same kubernetes cluster that you deployed Argo CD into.

``` bash
kubectl create namespace gitopsdemo-dev
kubectl create namespace gitopsdemo-qa
kubectl create namespace gitopsdemo-prod
```

#### Deploy
Let's start with the deploy application.  Click on 'Applications' in the navigation bar on the left.  Click on the 'New App' button.  We will create 'deploy-dev' application.  Notice that I am assigning this to teh deploy project and the gitopsdemo-dev namespace.  I have also added my github repo that I previously registered and I assigned the correct repo path to where the kustomization file resides.
![](pics/deploy-dev1.png)
![](pics/deploy-dev2.png)

Continue two additional applications for the two remaining namespaces naming them accordingly: deploy-qa, deploy-prod.  When you are done your application list for teh deploy project will look like this:
![](pics/deploy-app-list.png)

#### Start / Stop
Now let's create the applications for starting and stopping the postgres cluster in our start-stop project for all three namespaces.  Ensure that you select the correct namespace and the correct github repo path for each application.  Your completed application list for the start-stop project will look like this:
![](pics/start-stop-app-list.png)

#### Reset Password
The Postgres Operator (PGO) in CPK will automatically recreate a password in a secret it manages if that password is is blanked out ("").  We will use this feature in our next set of applications.  Create a reset-password application in the reset-password project for each namespace.  Again, be mindful to select the proper namespace and github repo path for each application.  These applications will be configure like the previous with one exception.  Check the 'Skip Schema Validation' checkbox.  Kubernetes does not like empty passwords in secrets.  However, the password will be immediately  regenerated with a new random password by the operator.
![](pics/reset-password-app.png)

Your completed application list for the reset-password project will look like this:
![](pics/reset-password-app-list.png)

## Gitops in Action
You have taken the time to configure Argo CD and setup all of the applications you require  to deploy Postgres clusters and perform day 2 operations.  Now its time to reap the benefits of your efforts.

### Deploy
Click on the 'Sync' button in the deploy-dev application in the deploy project:
![](pics/deploy-dev-synch-request.png)
Click on the 'Synchronize' button on the right panel.
Now to the same for the deploy-qa and deploy-prod applications.  You will notice that each application is now marked as "Synched'.
![](pics/deploy-apps-synched.png)
I can see that Postgres was deployed and backed when I request the pod list from the three namespaces:

``` bash
robertpacheco@Roberts-MBP kustomize % kubectl -n gitopsdemo-dev get pods
NAME                      READY   STATUS      RESTARTS   AGE
hippo-backup-vh2n-dpw8f   0/1     Completed   0          4m36s
hippo-pgdb-frxt-0         4/4     Running     0          5m30s
hippo-repo-host-0         2/2     Running     0          5m30s

robertpacheco@Roberts-MBP kustomize % kubectl -n gitopsdemo-qa get pods
NAME                      READY   STATUS      RESTARTS   AGE
hippo-backup-f6zq-sdj5z   0/1     Completed   0          3m43s
hippo-pgdb-56tb-0         5/5     Running     0          4m38s
hippo-repo-host-0         2/2     Running     0          4m38s

robertpacheco@Roberts-MBP kustomize % kubectl -n gitopsdemo-prod get pods
NAME                      READY   STATUS      RESTARTS   AGE
hippo-backup-jgtw-j9xwx   0/1     Completed   0          3m35s
hippo-pgdb-4lnh-0         5/5     Running     0          4m17s
hippo-pgdb-7lh7-0         5/5     Running     0          4m17s
hippo-repo-host-0         2/2     Running     0          4m16s
```

Notice the Postgres cluster differences between namespaces.
### Start / Stop
Let's stop the dev env