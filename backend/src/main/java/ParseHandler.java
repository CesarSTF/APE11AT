import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.io.PrintStream;
import java.io.StringReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class ParseHandler implements HttpHandler {
    @Override
    public void handle(HttpExchange exchange) throws java.io.IOException {
        if (!"POST".equals(exchange.getRequestMethod())) {
            sendJson(exchange, 405, "{\"error\":\"Método no permitido\"}");
            return;
        }

        String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json");
        exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");

        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        PrintStream captura = new PrintStream(baos, true, StandardCharsets.UTF_8);
        PrintStream originalOut = System.out;
        PrintStream originalErr = System.err;

        try {
            System.setOut(captura);
            System.setErr(captura);

            Lexer lexer = new Lexer(new StringReader(body));
            new parser(lexer).parse();

            String output = baos.toString(StandardCharsets.UTF_8).trim();
            String[] lines = output.isEmpty() ? new String[0] : output.split("\n");
            List<String> tokens = new ArrayList<>();
            StringBuilder extra = new StringBuilder();
            for (String line : lines) {
                String trimmed = line.trim();
                if (trimmed.startsWith("[TOKEN]")) {
                    tokens.add(trimmed.substring(7).trim());
                } else if (!trimmed.isEmpty()) {
                    if (extra.length() > 0) extra.append("\\n");
                    extra.append(trimmed);
                }
            }

            String json = buildJson("ok", "Análisis exitoso", body, tokens,
                    extra.length() > 0 ? extra.toString() : null);
            sendJson(exchange, 200, json);

        } catch (Exception e) {
            String output = baos.toString(StandardCharsets.UTF_8).trim();
            String[] lines = output.isEmpty() ? new String[0] : output.split("\n");
            List<String> tokens = new ArrayList<>();
            StringBuilder errorMsg = new StringBuilder();
            for (String line : lines) {
                String trimmed = line.trim();
                if (trimmed.startsWith("[TOKEN]")) {
                    tokens.add(trimmed.substring(7).trim());
                } else if (!trimmed.isEmpty()) {
                    if (errorMsg.length() > 0) errorMsg.append("\\n");
                    errorMsg.append(trimmed);
                }
            }

            String errorText = errorMsg.length() > 0 ? errorMsg.toString() : e.getMessage();
            String json = buildJson("error", traducir(errorText), body, tokens, null);
            sendJson(exchange, 200, json);

        } finally {
            System.setOut(originalOut);
            System.setErr(originalErr);
        }
    }

    private String buildJson(String status, String message, String input,
                             List<String> tokens, String diagnostico) {
        StringBuilder json = new StringBuilder();
        json.append("{\"status\":\"").append(status).append("\"");
        json.append(",\"message\":\"").append(escape(message)).append("\"");
        json.append(",\"input\":\"").append(escape(input)).append("\"");

        json.append(",\"tokens\":[");
        for (int i = 0; i < tokens.size(); i++) {
            if (i > 0) json.append(",");
            json.append("\"").append(escape(tokens.get(i))).append("\"");
        }
        json.append("]");

        if (diagnostico != null) {
            json.append(",\"diagnostico\":\"").append(escape(diagnostico)).append("\"");
        }
        json.append("}");
        return json.toString();
    }

    private void sendJson(HttpExchange exchange, int code, String json) throws java.io.IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(code, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    private String escape(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    private String traducir(String s) {
        String r = s.replace("Syntax error", "Error de sintaxis")
                .replace("instead expected token classes are", "los tokens esperados son")
                .replace("Couldn't repair and continue parse", "Expresión incompleta")
                .replace("Can't recover from previous error(s)", "No se puede recuperar del error");
        r = r.replace("[ID]", "[identificador]")
                .replace("[NUMBER]", "[número]")
                .replace("[PLUS]", "[+]")
                .replace("[MINUS]", "[-]")
                .replace("[ASSIGN]", "[=]");
        return r;
    }
}
