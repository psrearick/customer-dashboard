# Contributing to Customer Dashboard

Thank you for your interest in contributing to the Customer Dashboard project! This guide will help you understand how
to contribute effectively.

## Project Purpose

This is a demonstration platform for Laravel optimization techniques and architectural patterns, supporting blog content
at [philliprearick.com](https://philliprearick.com). Contributions should align with this educational mission.

## Types of Contributions

### Welcome Contributions

- **Bug fixes** - Issues with setup, Docker configurations, or application functionality
- **Documentation improvements** - Clearer explanations, typo fixes, or missing information
- **Setup improvements** - Better developer experience, additional helper scripts, or environment fixes
- **Performance monitoring** - Enhanced metrics, monitoring improvements, or measurement accuracy
- **Testing** - Better test coverage, test utilities, or validation scripts

### Contributions That Need Discussion First

- **New features** - The application complexity is intentionally managed to serve as a clear demonstration platform
- **Architectural changes** - Major changes could impact existing blog post demonstrations
- **New demonstration branches** - These typically correspond to planned blog content
- **Docker stack modifications** - Changes should maintain compatibility with existing blog posts

## Getting Started

### Development Setup

1. **Fork and clone your fork:**
   ```bash
   git clone https://github.com/your-username/customer-dashboard.git
   cd customer-dashboard
   ```

2. **Set up the development environment:**
   ```bash
   ./bin/setup
   ```

3. **Create a feature branch:**
   ```bash
   git checkout -b fix/description-of-fix
   # or
   git checkout -b docs/description-of-improvement
   ```

### Testing Your Changes

Before submitting a pull request:

1. **Test the setup process:**
   ```bash
   ./bin/app clean
   ./bin/setup
   # Verify everything works from scratch
   ```

2. **Test stack switching:**
   ```bash
   ./bin/app up -s frankenphp
   ./bin/app up -s octane
   ./bin/app up -s default
   # Ensure all stacks work with your changes
   ```

3. **Test helper commands:**
   ```bash
   ./bin/reset
   ./bin/branch main
   # Verify utilities still function correctly
   ```

## Contribution Guidelines

### Code Quality

- Follow Laravel coding standards and conventions
- Keep changes focused and minimal
- Include comments for complex logic
- Maintain consistency with existing code style

### Documentation

- Update relevant documentation for any changes
- Use clear, concise language
- Test documentation by following it yourself
- Keep the target audience in mind (blog readers getting started quickly)

### Docker and Infrastructure

- Test changes across different operating systems if possible
- Maintain resource efficiency (memory, CPU usage)
- Ensure changes work with existing helper scripts
- Document any new requirements or dependencies

### Branch and Commit Guidelines

- Use descriptive branch names: `fix/docker-memory-issue`, `docs/improve-setup-guide`
- Write clear commit messages explaining what and why
- Keep commits focused on a single logical change
- Include issue numbers in commit messages if applicable

## Pull Request Process

### Before Submitting

1. **Test thoroughly:**
    - Clean setup process works
    - All Docker stacks function correctly
    - Documentation is accurate and complete

2. **Check for conflicts:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

### Pull Request Format

**Title:** Clear, descriptive summary of the change

**Description should include:**

- What problem this solves or what it improves
- How you tested the changes
- Any breaking changes or new requirements
- Screenshots for UI changes or setup improvements

**Example:**

```
Fix Docker memory allocation issue on macOS

- Increases default memory requirements in documentation
- Updates docker-compose resource limits
- Adds memory check to setup script
- Tested on macOS with Docker Desktop 4.15+

Fixes #123
```

### Review Process

1. Automated checks must pass
2. Manual review by maintainer(s)
3. Testing on different platforms if infrastructure changes
4. Approval and merge

## Reporting Issues

### Bug Reports

Include:

- Operating system and Docker version
- Steps to reproduce the issue
- Expected vs. actual behavior
- Relevant log output or error messages
- Which Docker stack you were using

### Feature Requests

Before submitting:

- Check if it aligns with the project's educational mission
- Consider if it adds significant complexity
- Explain how it would benefit blog readers or contributors

## Development Environment Notes

### Resource Requirements

The project requires significant system resources for the full monitoring stack. When developing:

- Use `./bin/app up` for most development work
- Only use the performance stack when testing monitoring features
- Clean up regularly with `./bin/app clean` to free resources

### Common Development Tasks

```bash
# Working with application code
./bin/dev artisan tinker
./bin/dev artisan test
./bin/dev composer require package-name

# Testing Docker changes
./bin/app clean
./bin/app up
./bin/app validate

# Checking logs
./bin/app logs -s default -f
./bin/dev artisan log:clear
```

## Questions or Help

- **Setup issues:** Check [docs/troubleshooting.md](docs/troubleshooting.md)
- **Contribution questions:** Open a GitHub issue with the "question" label
- **Blog-related questions:** These are better directed to the blog itself

## Recognition

Contributors will be acknowledged in the project and may be mentioned in related blog posts where appropriate.

Thank you for helping make this demonstration platform better for the Laravel community!
