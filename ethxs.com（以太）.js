// let content = '';
// item.href = item.href.replace(/.*gotochapter\('(\d+)','(\d+)','(\d+)'\).*/, "/$1/$2/$3.html"); return item;
// @@@@@@
let content = data.querySelector('#contentinfo,#ChapterView>div:nth-child(3)>div');
if (!content)return data.body.innerText;
content.innerHTML = content.innerHTML.replace(/<br>/g, "\n");
content = content.innerText;
let pages = data.querySelectorAll(".chapterPages>a:not(.curr)");
if (pages) {
    let num = pages.length, cur = 0;
    content = [content];
    [].forEach.call(pages, (page, i) => {
        let url = page.href.replace(/.*\((\d+),(\d+),(\d+),(\d+)\).*/, "/$1/$2/$3_$4.html");
        fetch(url).then(r => r.text()).then(d => {
            let doc = document.implementation.createHTMLDocument('');
            doc.documentElement.innerHTML = d;
            let c = doc.querySelector('#contentinfo,#ChapterView>div:nth-child(3)>div');
            if (c) {
                c.innerHTML = c.innerHTML.replace(/<br>/g, "\n");
                content[i + 1] = c.innerText;
                if (++cur >= num) cb(content.join("\n"));
            }
        });
    });
    return false;
}
return content;
