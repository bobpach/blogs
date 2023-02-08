---
layout: post
created_at: 2023-02-08T15:00:00Z
published_at: 2023-02-08T15:00:00Z
author: Bob Pacheco
title: 'Postgres GitOps with Argo and Kubernetes'
description:
  'Curious about using Argo with application and database maintenance? Bob takes
  us through how to set up Argo with Crunchy Postgres for Kubernetes. The end
  result are some easy and simple GitOps for everyday tasks.'
image: 'https://imagedelivery.net/lPM0ntuwQfh8VQgJRu0mFg/ff1d4820-63d7-4a84-5180-fb025d646d00/public'
status: publish
published: true
meta:
  _edit_last: '1'
type: post
tags: Kubernetes
---

Postgres clusters should be updated regularly and have routine maintenance. This
regular maintenance is often referred to as “Day 2 operations” and can include a
wide variety of tasks like restarting services, resetting passwords, or updating
versions. Performing Day 2 operations can be complex and time consuming,
especially if you are supporting a large number of Postgres clusters.

With the adoption of GitOps and a little help from continuous delivery tools
like [Argo CD](https://argo-cd.readthedocs.io/en/stable/) you can simplify your
day 2 operations. The declarative nature of
[Crunchy Postgres for Kubernetes](https://www.crunchydata.com/products/crunchy-postgresql-for-kubernetes)
makes it a perfect candidate to integrate into the GitOps world. Let’s take a
look at how GitOps and Argo CD can help perform some of these routine Postgres
tasks.

The examples below assume that you have installed the
[Postgres Operator](https://www.crunchydata.com/developers/get-started/postgres-operator)
v5.2 or later in the same Kubernetes cluster that you will be deploying the
PostgreSQL clusters in.

## The “Git” in GitOps

In order to perform GitOps operations you must check-in your infrastructure
files to Git. In my GitHub repo I have a sample set of
[Kustomize files in a public repo](https://github.com/bobpach/blogs/tree/master/PostgresGitOps/gitops) that separates the files
into admin, base and overlay directories. This structure helps isolate files so
they can be independently run via [Kustomize](https://kustomize.io/) in Argo CD.  Feel free to fork and clone the repo if you would like to use those files to follow along.

In GitOps, Git is used as the ‘Single Source of Truth’ to manage all
infrastructure files. The files in my GitHub repo manage artifacts
to deploy the Postgres clusters and perform declarative day 2 operations on
them.

You can copy and paste the example files into your own files and check them in
to your git repo. Take care to replace the `<cluster_name>` place holder with
your own cluster name and use the same value in all of the example files.

## Argo CD

Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes. It
provides a UI and CLI that makes it easy to deploy and manage your applications
running on Kubernetes. To install Argo CD in your cluster simply run the
following:

```
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Additional details can be found in their
[getting started guide](https://argo-cd.readthedocs.io/en/stable/getting_started/).

To access the Argo CD UI I have changed the argocd-sever service from ClusterIP
to LoadBalancer. This provides an external IP that I can access from my browser.
You could also use a port forward or an ingress.

```
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

Once you have launched the Argo CD UI you can login. The initial password for
the **_admin_** account can be retrieved from the argocd-initial-admin-secret.

```
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

### Configuring ARGO CD

Now that you have logged in you are ready to start configuring Argo CD to deploy
and manage your Postgres cluster on Kubernetes.

### Add the Git Repository

You need to add your git repository to Argo CD. Click on ‘Settings’ in the
navigation bar on the left.

Now click on ‘Repositories’ and the ‘Connect Repo’ buttons. Provide the
necessary information and click ‘Save’. You should now have a connected repo. If
not, please review your settings and try again.

![argo-conntect-repo.png](https://imagedelivery.net/lPM0ntuwQfh8VQgJRu0mFg/9519b4cb-4730-46d0-23ff-454b86a03e00/original)

### Create the Projects

Argo CD uses projects to logically group applications. I created three projects:

- deploy

- reset-password

- start-stop

To create a project click on ‘Settings’ in the navigation bar on the left. Click
on ‘Project’ and then the ‘New Project’ button. Provide a project name and
description in the panel on the right and click create. Add your repo to ‘Source
Repositories’ and add your Kubernetes cluster to ‘Destinations’ as seen below.
Repeat the steps for each project you want to create.

![argo-deploy-app-list.png](https://imagedelivery.net/lPM0ntuwQfh8VQgJRu0mFg/0297b9d0-19ab-412a-61c7-1ce864446f00/original)

For this blog I deployed Argo CD in the same Kubernetes cluster that I am
deploying Postgres into. You can refer to the
[Argo CD Documentation](https://argo-cd.readthedocs.io/en/stable/) for other
deployment options.

## Creating Applications

Argo CD uses applications to perform declarative operations on its configured
Kubernetes cluster. We will create several applications to deploy Postgres
clusters and perform day 2 operations across three namespaces.

**_Operations_**

- Deploy Postgres
- Start Postgres
- Stop Postgres
- Reset Password
- Upgrade Postgres - Minor Version

Create the namespaces in the same Kubernetes cluster that you deployed Argo CD
into.

```
kubectl create namespace gitopsdemo-dev
kubectl create namespace gitopsdemo-qa
kubectl create namespace gitopsdemo-prod
```

### Deploy

Let’s start with the deploy application. Click on ‘Applications’ in the
navigation bar on the left. Click on the ‘New App’ button. We will create
‘deploy-dev’ application. Notice that I am assigning this to the deploy project
and the gitopsdemo-dev namespace. I have also added my github repo that I
previously registered and I assigned the correct repo path to where the
kustomization.yaml file resides.

Create two additional applications for the two remaining namespaces naming them
accordingly: deploy-qa, deploy-prod. When you are done your application list for
the deploy project will look like this:

![argo-deploy-projects.png](https://imagedelivery.net/lPM0ntuwQfh8VQgJRu0mFg/0297b9d0-19ab-412a-61c7-1ce864446f00/original)

**Start / Stop**

Now let’s create the applications for starting and stopping the Postgres cluster
in our start-stop project for all three namespaces. Ensure that you select the
correct namespace and the correct GitHub repo path for each application. Your
completed application list for the start-stop project will look like this:

![start-stop-app-list.png](https://imagedelivery.net/lPM0ntuwQfh8VQgJRu0mFg/e99361b9-53a5-436a-eee2-0ac717883f00/original)

**Reset Password**

The Postgres Operator (PGO) in CPK will automatically recreate a password in a
secret it manages if that password is blanked out (""). We will use this feature
in our next set of applications. Create a reset-password application in the
reset-password project for each namespace. Again, be mindful to select the
proper namespace and GitHub repo path for each application. These applications
will be configured like the previous with one exception. Check the ‘Skip Schema
Validation’ checkbox. Kubernetes does not like empty passwords in secrets.
However, the password will be immediately regenerated with a new random password
by the operator.

Your completed application list for the reset-password project will look like
this:

![argo-reset-password.png](https://imagedelivery.net/lPM0ntuwQfh8VQgJRu0mFg/4ea618d9-d1cb-4d64-f5c4-b0706126a800/original)

## GitOps in Action

You have taken the time to configure Argo CD and set up all of the applications
you require to deploy Postgres clusters and perform day 2 operations. Now you
can reap the benefits of your efforts.

### Deploy

Click on the ‘Sync’ button in the deploy-dev application in the deploy project:

![argo5.png](https://imagedelivery.net/lPM0ntuwQfh8VQgJRu0mFg/024b0a70-b17d-4c0d-9dee-77209884d500/public)

Click on the ‘Synchronize’ button on the right panel. Now do the same for the
deploy-qa and deploy-prod applications. You will notice that each application is
now marked as "Synched’.

I can see that Postgres was deployed and backed up when I request the pod list
from the three namespaces:

```
robertpacheco@Roberts-MBP kustomize % kubectl -n gitopsdemo-dev get pods
NAME                      READY   STATUS      RESTARTS   AGE
hippo-backup-vh2n-dpw8f   0/1     Completed   0          4m36s
hippo-pgdb-frxt-0         4/4     Running     0          5m30s
hippo-repo-host-0         2/2     Running     0          5m30s

robertpacheco@Roberts-MBP kustomize % kubectl -n gitopsdemo-qa get pods
NAME                      READY   STATUS      RESTARTS   AGE
hippo-backup-s8cw-85kn9   0/1     Completed   0          57s
hippo-pgdb-dfrr-0         5/5     Running     0          75s
hippo-pgdb-n6fh-0         5/5     Running     0          75s
hippo-repo-host-0         2/2     Running     0          75s

robertpacheco@Roberts-MBP kustomize % kubectl -n gitopsdemo-prod get pods
NAME                               READY   STATUS      RESTARTS   AGE
hippo-backup-qwzb-gkb75            0/1     Completed   0          51s
hippo-pgbouncer-7444dc559c-bsjmw   2/2     Running     0          67s
hippo-pgbouncer-7444dc559c-rk992   2/2     Running     0          67s
hippo-pgdb-b5hw-0                  5/5     Running     0          68s
hippo-pgdb-knvc-0                  5/5     Running     0          68s
hippo-repo-host-0                  2/2     Running     0          67s
```

Notice the Postgres cluster differences between namespaces. The gitopsdemo-dev
namespace has one Postgres pod with four containers, a repo host and a completed
backup job. The gitopsdemo-qa namespace has two Postgres pods with five
containers each, a repo host and a completed backup job. The gitopsdemo-prod
namespace has two pgBouncer pods in addition to the two postgres pods, repo host
and completed backup job.

The use of overlays allows you to standardize your base configuration and then
“overlay” that configuration with specific changes. Take a closer look at the
base and overlay yaml files we are using here to see what else has been changed
per instance.

### Start / Stop

The declarative nature of Crunchy PostgreSQL for Kubernetes works perfectly with
Argo CD to simplify Postgres Cluster deployments the GitOps way. Let’s stop the
dev Postgres cluster. Select the stop-dev application from the start-stop
project. Click on ‘Synch’ and then click on ‘Synchronize’ in the right panel.
You will notice that the application is now marked as ‘Synched’ and the dev pods
have been stopped. The backup job is still listed as completed. It was not
stopped because as a completed job it was not running.

```
robertpacheco@Roberts-MBP kustomize % kubectl -n gitopsdemo-dev get pods
NAME                      READY   STATUS      RESTARTS   AGE
hippo-backup-vh2n-dpw8f   0/1     Completed   0          58m
```

Now let’s start the dev Postgres cluster. Select the start-dev application from
the start-stop project. Click on ‘Synch’ and then click on ‘Synchronize’ in the
right panel. You will notice that the application is now marked as ‘Synched’ and
the dev pods have been started. You will also notice that the stop-dev job is
now marked as ‘OutOfSynch’.

```
robertpacheco@Roberts-MBP kustomize % kubectl -n gitopsdemo-dev get pods
NAME                      READY   STATUS      RESTARTS   AGE
hippo-backup-vh2n-dpw8f   0/1     Completed   0          61m
hippo-pgdb-frxt-0         4/4     Running     0          18s
hippo-repo-host-0         2/2     Running     0          18s
```

Try this with the qa and prod applications as well. It becomes very easy to
start or stop a Postgres cluster when needed using GitOps.

### Reset Password

Your security team has decided it is time to reset the password for the initial
user created at deploy time. First determine what the current password is so we
can validate that the change took place.

```
kubectl -n gitopsdemo-dev get secret <cluster_name-pguser-cluster_name> -o jsonpath="{.data.password}" | base64 -d; echo
```

Make a note of that password. Select the reset-password-dev application from the
reset-password project. Click on ‘Synch’ and then click on ‘Synchronize’ in the
right panel. In this case the status of the application stays listed as
‘OutOfSynch’ because the operator immediately assigned a new randomly generated
password after it was blanked out. Let’s run the same command again.

```
kubectl -n gitopsdemo-dev get secret <cluster_name-pguser-cluster_name> -o jsonpath="{.data.password}" | base64 -d; echo
```

You will notice that the password has been updated. Try this with the qa and
prod applications as well. Changing the Postgres password has never been easier!

### Postgres Upgrade

The PostgreSQL open source community typically releases a new major.minor
version of Postgres every quarter. These releases will contain bug and CVE
fixes. Crunchy Data updates their container images accordingly. It is considered
a best practice to take these updates into your Postgres clusters running on
Kubernetes as quickly as possible to apply CVE remediations and bug fixes.

Let’s check the current Postgres version in the dev cluster:

```
robertpacheco@Roberts-MBP ~ % kubectl exec -n gitopsdemo-dev hippo-pgdb-frxt-0 -c database -it -- bash
bash-4.4$ psql
psql (14.5)
Type "help" for help.

postgres=# select version();
                                                 version

---------------------------------------------------------------------------------------------------------
 PostgreSQL 14.5 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 8.5.0 20210514 (Red Hat 8.5.0-10), 64-bit
(1 row)
```

Using Argo CD and GitOps we will declaratively state our intent by updating the
images in our deployment artifacts in git. Let’s take a closer look.

In the postgres.yaml file in our base/postgres directory we have two images:

- Postgres: image:
  registry.developers.crunchydata.com/crunchydata/crunchy-postgres:ubi8-14.5-1
- pgBackrest: image:
  registry.developers.crunchydata.com/crunchydata/crunchy-pgbackrest:ubi8-2.40-1

Update that file with the latest images for the same major version:

- Postgres: image:
  registry.developers.crunchydata.com/crunchydata/crunchy-postgres:ubi8-14.6-0
- pgBackrest: image:
  registry.developers.crunchydata.com/crunchydata/crunchy-pgbackrest:ubi8-2.41-0

Once you check these changes into your GitHub repo click the ‘Refresh Apps’
button at the top of the applications screen for the deploy project. You will
see that the applications in the deploy project are now listed as ‘OutOfSynch’.

Select the deploy-dev application from the deploy project. Click on ‘Synch’ and
then click on ‘Synchronize’ in the right panel.

When you synchronize the Postgres Operator will bring down the repo host and a
Postgres replica pod. Those pods will immediately be restarted with the new
images. Each Postgres replica pod will be upgraded one at a time until just the
primary pod is left. The primary pod will then automatically failover to a
recently upgraded replica pod and will then restart with the new image coming
back up as a replica. If you only have one Postgres pod, as we do in the dev
cluster, that pod immediately gets upgraded.

You will notice that the deploy-dev application is now marked asd ‘Synched’.

Now check the Postgres version:

```
robertpacheco@Roberts-MBP ~ % kubectl exec -n gitopsdemo-dev hippo-pgdb-frxt-0 -c database -it -- bash
bash-4.4$ psql
psql (14.6)
Type "help" for help.

postgres=# select version();
                                                 version

---------------------------------------------------------------------------------------------------------
 PostgreSQL 14.6 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 8.5.0 20210514 (Red Hat 8.5.0-15), 64-bit
(1 row)
```

Using this approach allows you to test your upgrade in the dev cluster before
applying it to qa and prod. Once you feel confident that the Postgres cluster
and its consumers are working as expected you can synchronize the deploy-qa
application and then once qa testing is complete you can synchronize the
deploy-prod application.

You changed the images in one file and were able to upgrade all three Postgres
clusters thanks to Argo CD and GitOps.

## Summary

[Crunchy Postgres for Kubernetes](https://www.crunchydata.com/products/crunchy-postgresql-for-kubernetes)
is a powerful tool to rapidly deploy Postgres clusters in any Kubernetes
environment. The declarative nature of CPK makes it a perfect candidate for
GitOps. Administrative responsibilities don’t stop once the deployment is
complete. Being able to perform Day 2 operations at scale is crucial to ensure
the security, stability and performance of your Postgres clusters. Argo CD and
GitOps can simplify the day to day operations needed by your enterprise
deployments. This is just a small sample of what you can achieve with GitOps. If
there are Kubernetes tasks that you run frequently or run against multiple
clusters, GitOps may be worth a look.
