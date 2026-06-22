.PHONY: all run run-java run-python compile clean test stop

DIR = Analizar_en_java

all: compile

compile:
	cd $(DIR) && mvn compile

run: stop compile
	@echo "=== Arrancando servidor Java en :8080 ==="
	cd $(DIR) && mvn -pl backend -q exec:java > /tmp/ape11at-java.log 2>&1 &
	echo $$! > /tmp/ape11at-java.pid
	@sleep 3
	@echo "=== Arrancando servidor Python en :8081 ==="
	cd $(DIR) && python3 backend_python/server.py > /tmp/ape11at-python.log 2>&1 &
	echo $$! > /tmp/ape11at-python.pid
	@sleep 1
	@echo ""
	@echo "============================================"
	@echo "  Java  → http://localhost:8080"
	@echo "  Python → http://localhost:8081"
	@echo "============================================"
	@echo "  Usa 'make stop' para detener ambos"

run-java: compile
	cd $(DIR) && mvn -pl backend -q exec:java

run-python:
	cd $(DIR) && python3 backend_python/server.py

stop:
	@-kill `cat /tmp/ape11at-java.pid 2>/dev/null` 2>/dev/null; rm -f /tmp/ape11at-java.pid; true
	@-kill `cat /tmp/ape11at-python.pid 2>/dev/null` 2>/dev/null; rm -f /tmp/ape11at-python.pid; true
	@echo "Servidores detenidos"

test: stop compile
	@echo "=== Iniciando servidor Java ==="
	cd $(DIR) && mvn -pl backend -q exec:java > /tmp/ape11at-java.log 2>&1 &
	echo $$! > /tmp/ape11at-java.pid
	@sleep 3
	@echo "=== Prueba: válido ==="
	curl -s -X POST http://localhost:8080/api/parse -d "x = 10 + 5" | python3 -m json.tool
	@echo ""
	@echo "=== Prueba: error sintáctico ==="
	curl -s -X POST http://localhost:8080/api/parse -d "x = " | python3 -m json.tool
	@echo ""
	@echo "=== Deteniendo servidor ==="
	make stop

clean:
	cd $(DIR) && mvn clean
	rm -rf __pycache__ *.pyc
