import { BS_LAB_FILES } from "../bs_lab_bundle";

// Lazy, cached Pyodide runtime (kept warm across requests when the worker stays hot)
let pyodideReady: Promise<any> | null = null;

// One-time bootstrapping: write python package files + import
let bootstrapped = false;

async function getPyodide(): Promise<any> {
    if (!pyodideReady) {
        pyodideReady = (async () => {
            // Cloudflare Worker runtime: use Pyodide ESM bundle from CDN (do NOT use npm "pyodide")
            const pyodideModule = await import(
        /* @vite-ignore */ "https://cdn.jsdelivr.net/pyodide/v0.26.0/full/pyodide.mjs"
            );

            const pyodide = await pyodideModule.loadPyodide({
                indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.0/full/",
            });

            return pyodide;
        })();
    }

    return pyodideReady;
}

async function bootstrapPyPackage(pyodide: any): Promise<void> {
    if (bootstrapped) return;

    // Setup python import path + package dir
    pyodide.runPython(`
import os, sys
BASE = "/home/pyodide"
PKG_DIR = os.path.join(BASE, "bs_lab")
if BASE not in sys.path:
    sys.path.append(BASE)
os.makedirs(PKG_DIR, exist_ok=True)
`);

    // Write packaged python files once
    for (const [filename, content] of Object.entries(BS_LAB_FILES)) {
        pyodide.FS.writeFile(`/home/pyodide/bs_lab/${filename}`, String(content));
    }

    // Import once to validate package and warm caches
    await pyodide.runPythonAsync(`import bs_lab.api`);

    bootstrapped = true;
}

export const onRequestPost = async (context: any) => {
    try {
        const req: Request = context.request;

        // Parse request body as text (your Python expects JSON string)
        const payload = await req.text();

        const pyodide = await getPyodide();
        await bootstrapPyPackage(pyodide);

        // Pass data safely into Python
        pyodide.globals.set("payload_json", payload);

        // Compute (run_compute returns a JSON string)
        const result = await pyodide.runPythonAsync(`
import bs_lab.api
bs_lab.api.run_compute(payload_json)
`);

        return new Response(result, {
            status: 200,
            headers: {
                "Content-Type": "application/json; charset=utf-8",
                "Cache-Control": "no-store",
            },
        });
    } catch (err: any) {
        const message =
            err?.stack ? String(err.stack) : err?.toString ? String(err.toString()) : String(err);

        return new Response(JSON.stringify({ error: message }), {
            status: 500,
            headers: {
                "Content-Type": "application/json; charset=utf-8",
                "Cache-Control": "no-store",
            },
        });
    }
};

export const onRequestGet = async () => {
    return new Response("Method Not Allowed", {
        status: 405,
        headers: { Allow: "POST" },
    });
};
// redeploy
