import { loadPyodide } from 'pyodide';
import { BS_LAB_FILES } from '../bs_lab_bundle';

let pyodide: any = null;

export const onRequestPost = async (context: any) => {
    try {
        const req = context.request;
        const payload = await req.text();

        if (!pyodide) {
            // Load Pyodide from CDN (lightweight loader, fetches wasm)
            pyodide = await loadPyodide({
                // Use a fixed version to ensure stability
                indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/"
            });

            // Setup filesystem
            // We write the package to the filesystem so we can import it normally
            // 'bs_lab' package
            pyodide.runPython(`
        import os
        import sys
        if '/home/pyodide' not in sys.path:
            sys.path.append('/home/pyodide')
        os.makedirs('/home/pyodide/bs_lab', exist_ok=True)
      `);

            // Write all files
            for (const [filename, content] of Object.entries(BS_LAB_FILES)) {
                pyodide.FS.writeFile(`/home/pyodide/bs_lab/${filename}`, content);
            }

            // Pre-import
            await pyodide.runPythonAsync(`
        import bs_lab.api
      `);
        }

        // Pass data safely
        pyodide.globals.set("payload_json", payload);

        // Compute
        const result = await pyodide.runPythonAsync(`
      import bs_lab.api
      bs_lab.api.run_compute(payload_json)
    `);

        // Return response
        return new Response(result, {
            headers: { "Content-Type": "application/json" }
        });

    } catch (err: any) {
        return new Response(JSON.stringify({ error: err.toString() }), {
            status: 500,
            headers: { "Content-Type": "application/json" }
        });
    }
}

export const onRequestGet = () => {
    return new Response("Method Not Allowed", { status: 405 });
}
