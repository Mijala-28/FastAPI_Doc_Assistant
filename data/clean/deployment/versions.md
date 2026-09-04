# About FastAPI versions

**FastAPI** is already being used in production in many applications and systems. And the test coverage is kept at 100%. But its development is still moving quickly.

New features are added frequently, bugs are fixed regularly, and the code is still continuously improving.

That's why the current versions are still `0.x.x`, this reflects that each version could potentially have breaking changes. This follows the [Semantic Versioning](https://semver.org/) conventions.

You can create production applications with **FastAPI** right now (and you have probably been doing it for some time), you just have to make sure that you use a version that works correctly with the rest of your code.

## Pin your `fastapi` version

The first thing you should do is to "pin" the version of **FastAPI** you are using to the specific latest version that you know works correctly for your application.

For example, let's say you are using version `0.112.0` in your app.

If you use a `requirements.txt` file you could specify the version with:

```txt
fastapi[standard]==0.112.0
```

that would mean that you would use exactly the version `0.112.0`.

Or you could also pin it with:

```txt
fastapi[standard]>=0.112.0,=0.45.0,=2.7.0,<3.0.0
```
