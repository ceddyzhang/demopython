run:
	python hello_world.py

test:
	python -c "import hello_world; assert hello_world.greet() == 'Hello, World!'"
	python -c "import hello_world; assert hello_world.greet() == 'Hello, Alice!'"
help:
	@echo "Makefile commands:"
	@echo "  run   - Run the hello-world.py script"
	@echo "  test  - Test the greet function in hello-world.py"