# Customer Dashboard Demo Application

## Introduction

This is a demonstration platform for Laravel patterns and techniques, supporting
the content of [Phillip Rearick's blog](https://philliprearick.com). The blog
discusses optimization techniques, architectural patterns, and production-ready
enterprise solutions.

While code snippets and conceptual explanations are helpful, sometimes you only
understand something after seeing it in practice, manipulating it, and using it
yourself. That's what this project is about. It goes beyond basic examples
and demonstrates the topics discussed in the blog in the context of a complete
multi-tenant SaaS platform built with Laravel, React, and Inertia.js.

## Post Source Code

Many blog posts contain a link to the source code used in the article. Maybe
that's how you got here. Most of these links go to specific branches associated
with the source articles, while others may link to the `main` branch. If the branch
you are on has an associated blog post, it will have its own README file,
[README.blog.md](README.blog.md), which provides instructions for the specific
article.

If the post does not have a README, or the README does not provide specific
instructions on how to get started, follow along with the [quick start](#quick-start)
section below or head over to the [getting started](docs/getting-started.md) guide
for more details.


## Quick Start

```bash
# Clone the repository
git clone https://github.com/psrearick/customer-dashboard.git
cd customer-dashboard

# Start traditional environment
./bin/stack up traditional -d

# Set up application with comprehensive monitoring
./bin/dev artisan key:generate
./bin/dev artisan migrate --seed
./bin/dev composer install
./bin/dev npm install && ./bin/dev npm run build

# Access the application
open http://localhost              # Main application
```

## Documentation

You'll find the documentation [here](docs/README.md).


If you have found a bug, are stuck using the project, or have a question,
[create an issue on GitHub](https://github.com/psrearick/customer-dashboard/issues).

## Contributing

Please see [CONTRIBUTING](CONTRIBUTING.md) for details.

## License

This project is open-sourced software licensed under the [MIT license](LICENSE).