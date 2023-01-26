# Day 2 Operations for PostgreSQL Clusters on Kubernetes at Scale

It is critical that Postgres clusters are optimized, updated regularly and have routine maintenance to ensure that the environment stays stable, secure and performant.  The process of achieving this is often referred to as Day 2 operations.  Performing Day 2 operations can be complex and time consuming; especially if you are supporting a large number Postgres clusters.

To date, infrastructure management has mostly been a manual process.  However, with the adoption of [Gitops](https://about.gitlab.com/topics/gitops/) and a little help from a continuos delivery tool like [Argo CD](https://argo-cd.readthedocs.io/en/stable/) you can reduce the complexity and even automate your Day 2 operations. The declarative nature of Crunchy Postgres for Kubernetes (CPK) makes it a perfect candidate for gitops. Let's take a look at how gitops and Argo CD can help perform Day 2 Operations on your Crunchy Data Postgres cluster on kubernetes.

# The "Git" in Gitops

In order to perform gitops operations you must check-in your infrastructure files in Git.  Im my github repo I have a file structure that separates the files into admin, base and overlay directories. This structure helps isolate files so they can be independently run via [Kustomize](https://kustomize.io/) in Argo CD.



- PostgresGitOps:
  - gitops:
    - admin:
      - reset-hippo-password:
        <details><summary>- kustomization.yaml</summary>

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



In gitops, Git is used as the [Single Source of Truth](https://en.wikipedia.org/wiki/Single_source_of_truth) to manage all infrastructure files.  The files used in the preceding examples manage artifacts to deploy the Postgres clusters and perform declarative Day 2 Operations on the those clusters. You can copy and paste the example files into your own files and check them in to your git repo.</br>

***Note:*** Ensure that you replace the ```<cluster_name>``` place holder with your own cluster name and use the same value in all of the example files.