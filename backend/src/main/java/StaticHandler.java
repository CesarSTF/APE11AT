import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Map;

public class StaticHandler implements HttpHandler {
    private static final Map<String, String> MIME = Map.of(
        "html", "text/html",
        "js",   "application/javascript",
        "css",  "text/css",
        "json", "application/json",
        "png",  "image/png",
        "svg",  "image/svg+xml",
        "ico",  "image/x-icon"
    );

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        String path = exchange.getRequestURI().getPath();
        if (path.equals("/api/parse")) return;

        if (path.equals("/") || path.isEmpty()) path = "/index.html";

        String cwd = System.getProperty("user.dir");
        File dir;
        File cand1 = new File(cwd, "frontend/src/main/webapp");
        File cand2 = new File(cwd, "../frontend/src/main/webapp");
        if (cand1.isDirectory()) dir = cand1;
        else if (cand2.isDirectory()) dir = cand2;
        else { send404(exchange); return; }

        File file = new File(dir, path).getCanonicalFile();
        if (!file.getPath().startsWith(dir.getCanonicalPath()) || !file.isFile()) {
            send404(exchange);
            return;
        }

        String ext = "";
        int i = file.getName().lastIndexOf('.');
        if (i > 0) ext = file.getName().substring(i + 1);

        String mime = MIME.getOrDefault(ext, "application/octet-stream");
        exchange.getResponseHeaders().add("Content-Type", mime);
        exchange.sendResponseHeaders(200, file.length());

        try (OutputStream os = exchange.getResponseBody();
             FileInputStream fis = new FileInputStream(file)) {
            fis.transferTo(os);
        }
    }

    private void send404(HttpExchange exchange) throws IOException {
        String msg = "<h1>404</h1>";
        byte[] b = msg.getBytes();
        exchange.sendResponseHeaders(404, b.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(b);
        }
    }
}
