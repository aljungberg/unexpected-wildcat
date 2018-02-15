## Build

```bash
docker build -t unexpected-wildcat .
```

## Develop

```bash
docker run --rm --name unexpected-wildcat -v `pwd`:/usr/src/app:ro -e PHABRICATOR_API_URL="https://truecode.trueship.com/api/" -e PHABRICATOR_API_TOKEN="cli-123" -it unexpected-wildcat
```

## Test

```bash
docker run --rm --name unexpected-wildcat -e PHABRICATOR_API_URL="https://truecode.trueship.com/api/" -e PHABRICATOR_API_TOKEN="cli-123" -it unexpected-wildcat nosetests
```

## Serve

```bash
docker run --rm --name unexpected-wildcat -e PHABRICATOR_API_URL="https://truecode.trueship.com/api/" -e PHABRICATOR_API_TOKEN="cli-123" -it unexpected-wildcat
```
