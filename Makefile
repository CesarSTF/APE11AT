.PHONY: all compile run test api clean

all: compile

compile:
	mvn compile

run: clean
	mvn -pl backend compile exec:java

test: clean
	@echo "=== Iniciando servidor ==="
	mvn -pl backend -q exec:java & \
	PID=$$!; \
	echo "Servidor PID: $$PID"; \
	echo "Esperando..."; \
	for i in 1 2 3 4 5; do \
		sleep 1; \
		curl -sf http://localhost:8080/ > /dev/null 2>&1 && break; \
	done; \
	echo "=== Parse válido ==="; \
	curl -s -X POST http://localhost:8080/api/parse -d "x = 10 + 5" | python3 -m json.tool; \
	echo ""; \
	echo "=== Error sintáctico ==="; \
	curl -s -X POST http://localhost:8080/api/parse -d "x = " | python3 -m json.tool; \
	echo ""; \
	echo "=== Error léxico ==="; \
	curl -s -X POST http://localhost:8080/api/parse -d "x = @10" | python3 -m json.tool; \
	echo ""; \
	echo "=== Deteniendo servidor ==="; \
	kill $$PID 2>/dev/null; true

api:
	curl -s -X POST http://localhost:8080/api/parse -d "$$(cat)" | python3 -m json.tool

clean:
	mvn clean
