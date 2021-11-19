let progressBar;
$(window).on('load', () => {progressBar = document.getElementById("download-progress-bar")});
function download_playlist() {
    progressBar.setAttribute("value", 1);
    progressBar.style.display = "block";
    progressBar.setAttribute("max", beatmap_ids.length);
    let files = [];
    beatmap_ids.forEach(([id, name]) => {
        let xhr = new XMLHttpRequest();
        let param = btoa(JSON.stringify({server: 1, beatmapsetid: parseInt(id)}));
        xhr.open("GET", `https://api.nerina.pw/download?b=${param}`, true);
        xhr.responseType = "blob";

        xhr.onload = () => {
            files.push([`${id} ${name}.osz`, xhr.response]);
            progressBar.setAttribute("value", parseInt(progressBar.getAttribute("value")) + 1);
            if(files.length === beatmap_ids.length) {
                zip_playlist(files);
            }
        }
        xhr.send();
    });
}

async function zip_playlist(files) {
    progressBar.removeAttribute("value");
    progressBar.removeAttribute("max");
    let zipWriter = new zip.ZipWriter(new zip.BlobWriter("application/zip"));
    for (let file of files) {
        try {
            await zipWriter.add(file[0], new zip.BlobReader(file[1]));
        } catch {
            await zipWriter.add(`Error`, new zip.BlobReader(file[1]));
        }
    }
    let zipBlob = await zipWriter.close();
    downloadBlob(zipBlob, `${document.title.replace(" | osulist", "")}.zip`);
    progressBar.style.display = "none";
}

function downloadBlob(blob, name) {
    const blobUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = name;

    document.body.appendChild(link);
    link.dispatchEvent(
        new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        })
    );
    document.body.removeChild(link);
}
