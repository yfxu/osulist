let progressBar = document.getElementById("download-progress-bar");
function download_playlist() {
    progressBar.setAttribute("value", 1);
    progressBar.style.display = "block";
    progressBar.setAttribute("max", beatmap_ids.length);
    let files = [];
    beatmap_ids.forEach(id => {
        let xhr = new XMLHttpRequest();
        xhr.open("GET", `https://api.chimu.moe/v1/download/${id}?n`, true);
        xhr.responseType = "blob";

        xhr.onload = () => {
            files.push([decodeURI(xhr.responseURL.split("?filename=")[1]), xhr.response, id]);
            console.log(`Downloaded ${files.length} / ${beatmap_ids.length}`);
            //remember to add
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
            await zipWriter.add(file[0] != "undefined" ? file[0] : `Error_map_${file[2]}`, new zip.BlobReader(file[1]));
        } catch {
            await zipWriter.add(`Error_map_${file[2]}`, new zip.BlobReader(file[1]));
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