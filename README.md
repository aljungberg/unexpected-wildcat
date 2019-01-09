## Build

```bash
bin/ci_setup.sh
```

## Develop

```bash
docker run --rm --name unexpected-wildcat -v `pwd`:/usr/src/app:ro -e PHABRICATOR_API_URL="https://truecode.trueship.com/api/" -e PHABRICATOR_API_TOKEN="cli-123" -it gcr.io/rc-apps-images/unexpected-wildcat

# set up an ngrok tunnel to your local instance
docker run --rm -it --link unexpected-wildcat wernight/ngrok ngrok http unexpected-wildcat:8080
```

## Test

```bash
bin/ci_test.sh
```

## Serve

```bash
docker run --rm --name unexpected-wildcat -e PHABRICATOR_API_URL="https://truecode.trueship.com/api/" -e PHABRICATOR_API_TOKEN="api-123" -it gcr.io/rc-apps-images/unexpected-wildcat
```
