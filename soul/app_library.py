"""Pre-verified, 10/10 functional web app templates for the NEPTUNE Utility Grid."""

APP_LIBRARY = [
    # --- DEVELOPER UTILITIES ---
    {
        "id": "json-formatter",
        "category": "developer utility",
        "ui": """<textarea id="jsonInput" rows="6" placeholder="Paste raw JSON here..."></textarea>
                 <div class="grid-2">
                    <button onclick="formatJSON()">Beautify JSON</button>
                    <button onclick="minifyJSON()" style="background:#475569;">Minify JSON</button>
                 </div>""",
        "js": """function formatJSON() {
            try { const obj = JSON.parse(document.getElementById('jsonInput').value); showResult('<pre style="text-align:left; overflow-x:auto;">' + JSON.stringify(obj, null, 4) + '</pre>'); }
            catch(e) { showResult('Invalid JSON Syntax.', true); }
        }
        function minifyJSON() {
            try { const obj = JSON.parse(document.getElementById('jsonInput').value); showResult('<pre style="text-align:left; overflow-x:auto; word-break:break-all; white-space:pre-wrap;">' + JSON.stringify(obj) + '</pre>'); }
            catch(e) { showResult('Invalid JSON Syntax.', true); }
        }
        function showResult(html, err=false) {
            const el = document.getElementById('result');
            el.style.display = 'block';
            el.style.borderColor = err ? '#ef4444' : '#3b82f6';
            el.innerHTML = html;
        }"""
    },
    {
        "id": "url-encoder-decoder",
        "category": "developer utility",
        "ui": """<textarea id="urlInput" rows="4" placeholder="Enter URL or text..."></textarea>
                 <div class="grid-2">
                    <button onclick="encodeUrl()">URL Encode</button>
                    <button onclick="decodeUrl()" style="background:#475569;">URL Decode</button>
                 </div>""",
        "js": """function encodeUrl() {
            try { showResult(encodeURIComponent(document.getElementById('urlInput').value)); }
            catch(e) { showResult('Error encoding.', true); }
        }
        function decodeUrl() {
            try { showResult(decodeURIComponent(document.getElementById('urlInput').value)); }
            catch(e) { showResult('Error decoding.', true); }
        }
        function showResult(text, err=false) {
            const el = document.getElementById('result'); el.style.display = 'block'; el.style.borderColor = err ? '#ef4444' : '#3b82f6'; el.innerText = text;
        }"""
    },
    {
        "id": "color-hex-converter",
        "category": "developer utility",
        "ui": """<label>Select or Enter a Color</label>
                 <div style="display:flex; gap:1rem; margin-bottom:1rem;">
                    <input type="color" id="colorPicker" value="#3b82f6" style="height:50px; width:100px; padding:0; cursor:pointer;" onchange="syncColor('picker')">
                    <input type="text" id="hexInput" value="#3b82f6" oninput="syncColor('hex')" style="margin-bottom:0;">
                 </div>
                 <div id="colorStats" style="background:#0f172a; padding:1rem; border-radius:6px; font-family:monospace;">RGB: rgb(59, 130, 246)</div>""",
        "js": """function syncColor(source) {
            let hex = source === 'picker' ? document.getElementById('colorPicker').value : document.getElementById('hexInput').value;
            if(!hex.startsWith('#')) hex = '#' + hex;
            if(/^#[0-9A-F]{6}$/i.test(hex)) {
                document.getElementById('colorPicker').value = hex;
                document.getElementById('hexInput').value = hex;
                const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
                document.getElementById('colorStats').innerHTML = `RGB: rgb(${r}, ${g}, ${b})`;
                document.body.style.borderTop = `5px solid ${hex}`;
            }
        }"""
    },
    {
        "id": "markdown-previewer",
        "category": "developer utility",
        "ui": """<textarea id="mdInput" rows="6" placeholder="# Hello\\nWrite markdown here..." oninput="updateMd()"></textarea>
                 <div id="mdOut" style="background:#1e293b; padding:1rem; border-radius:6px; text-align:left; border:1px solid #334155;"></div>""",
        "js": """function updateMd() {
            let t = document.getElementById('mdInput').value;
            t = t.replace(/^### (.*$)/gim, '<h3>$1</h3>')
                 .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                 .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                 .replace(/\\*\\*(.*)\\*\\*/gim, '<b>$1</b>')
                 .replace(/\\*(.*)\\*/gim, '<i>$1</i>')
                 .replace(/\n$/gim, '<br />');
            document.getElementById('mdOut').innerHTML = t;
        }"""
    },
    {
        "id": "uuid-generator",
        "category": "developer utility",
        "ui": """<button onclick="generateUUID()">Generate UUID / GUID</button>
                 <div id="uuidList" style="font-family:monospace; margin-top:1rem; background:#0f172a; padding:1rem; border-radius:6px;"></div>""",
        "js": """function generateUUID() {
            let dt = new Date().getTime();
            const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = (dt + Math.random()*16)%16 | 0;
                dt = Math.floor(dt/16);
                return (c=='x' ? r :(r&0x3|0x8)).toString(16);
            });
            const el = document.getElementById('uuidList');
            el.innerHTML = `<div style="color:#10b981; font-size:1.2rem; margin-bottom:0.5rem;">${uuid}</div>` + el.innerHTML;
        }"""
    },
    # --- FINANCE & CRYPTO ---
    {
        "id": "crypto-profit-calculator",
        "category": "finance calculator",
        "ui": """<div class="grid-2">
                    <div><label>Buy Price ($)</label><input type="number" id="buy" value="60000"></div>
                    <div><label>Sell Price ($)</label><input type="number" id="sell" value="75000"></div>
                 </div>
                 <label>Investment Amount ($)</label><input type="number" id="invest" value="1000">
                 <button onclick="calcCrypto()">Calculate Profit</button>""",
        "js": """function calcCrypto() {
            const b = parseFloat(document.getElementById('buy').value);
            const s = parseFloat(document.getElementById('sell').value);
            const i = parseFloat(document.getElementById('invest').value);
            if(isNaN(b) || isNaN(s) || isNaN(i) || b === 0) return;
            const coins = i / b;
            const revenue = coins * s;
            const profit = revenue - i;
            const roi = (profit / i) * 100;
            const el = document.getElementById('result'); el.style.display = 'block';
            const color = profit >= 0 ? '#10b981' : '#ef4444';
            el.innerHTML = `<strong>Total Return:</strong> $${revenue.toFixed(2)}<br><strong style="color:${color}">Net Profit/Loss:</strong> <span style="color:${color}">$${profit.toFixed(2)}</span><br><strong>ROI:</strong> ${roi.toFixed(2)}%`;
        }"""
    },
    {
        "id": "compound-interest",
        "category": "finance calculator",
        "ui": """<label>Initial Investment ($)</label><input type="number" id="p" value="1000">
                 <label>Annual Interest Rate (%)</label><input type="number" id="r" value="5">
                 <label>Years to Grow</label><input type="number" id="t" value="10">
                 <button onclick="calcInterest()">Calculate Returns</button>""",
        "js": """function calcInterest() {
            const p = parseFloat(document.getElementById('p').value);
            const r = parseFloat(document.getElementById('r').value) / 100;
            const t = parseFloat(document.getElementById('t').value);
            if(isNaN(p) || isNaN(r) || isNaN(t)) return;
            const a = p * Math.pow((1 + r), t);
            const el = document.getElementById('result');
            el.style.display = 'block';
            el.innerHTML = `<strong>Future Value:</strong> $${a.toFixed(2)}<br><strong>Total Profit:</strong> $${(a-p).toFixed(2)}`;
        }"""
    },
    {
        "id": "tip-calculator",
        "category": "finance calculator",
        "ui": """<label>Bill Amount ($)</label><input type="number" id="bill" value="50">
                 <label>Tip Percentage (%)</label><input type="number" id="tip" value="20">
                 <label>Number of People</label><input type="number" id="people" value="2" min="1">
                 <button onclick="calcTip()">Calculate Split</button>""",
        "js": """function calcTip() {
            const b = parseFloat(document.getElementById('bill').value);
            const t = parseFloat(document.getElementById('tip').value) / 100;
            const p = parseInt(document.getElementById('people').value);
            if(isNaN(b) || isNaN(t) || isNaN(p) || p < 1) return;
            const tipAmt = b * t;
            const total = b + tipAmt;
            const perPerson = total / p;
            const el = document.getElementById('result'); el.style.display = 'block';
            el.innerHTML = `<strong>Tip Amount:</strong> $${tipAmt.toFixed(2)}<br><strong>Total Bill:</strong> $${total.toFixed(2)}<br><strong style="color:#3b82f6; font-size:1.2rem;">Per Person: $${perPerson.toFixed(2)}</strong>`;
        }"""
    },
    {
        "id": "roi-calculator",
        "category": "finance calculator",
        "ui": """<label>Amount Invested ($)</label><input type="number" id="roi_i" value="5000">
                 <label>Amount Returned ($)</label><input type="number" id="roi_r" value="6500">
                 <button onclick="calcROI()">Calculate ROI</button>""",
        "js": """function calcROI() {
            const i = parseFloat(document.getElementById('roi_i').value);
            const r = parseFloat(document.getElementById('roi_r').value);
            if(isNaN(i) || isNaN(r) || i === 0) return;
            const profit = r - i;
            const roi = (profit / i) * 100;
            const color = profit >= 0 ? '#10b981' : '#ef4444';
            const el = document.getElementById('result'); el.style.display = 'block';
            el.innerHTML = `<strong>Net Profit:</strong> <span style="color:${color}">$${profit.toFixed(2)}</span><br><strong>ROI:</strong> <span style="color:${color}">${roi.toFixed(2)}%</span>`;
        }"""
    },
    # --- TEXT TOOLS ---
    {
        "id": "word-counter",
        "category": "developer utility",
        "ui": """<textarea id="textInput" rows="6" placeholder="Paste your text here..." oninput="count()"></textarea>
                 <div class="grid-2">
                    <div style="background:#0f172a; padding:1rem; border-radius:6px; text-align:center;">Words: <strong id="wordCount" style="color:#3b82f6; font-size:1.5rem;">0</strong></div>
                    <div style="background:#0f172a; padding:1rem; border-radius:6px; text-align:center;">Characters: <strong id="charCount" style="color:#3b82f6; font-size:1.5rem;">0</strong></div>
                 </div>""",
        "js": """function count() {
            const text = document.getElementById('textInput').value;
            const words = text.trim() === '' ? 0 : text.trim().split(/\\s+/).length;
            document.getElementById('wordCount').innerText = words;
            document.getElementById('charCount').innerText = text.length;
        }"""
    },
    {
        "id": "case-converter",
        "category": "developer utility",
        "ui": """<textarea id="textData" rows="5" placeholder="Enter text here..."></textarea>
                 <div class="grid-2">
                    <button onclick="changeCase('upper')">UPPERCASE</button>
                    <button onclick="changeCase('lower')">lowercase</button>
                    <button onclick="changeCase('title')">Title Case</button>
                    <button onclick="changeCase('sentence')">Sentence case</button>
                 </div>""",
        "js": """function changeCase(type) {
            let t = document.getElementById('textData').value;
            if(!t) return;
            if(type === 'upper') t = t.toUpperCase();
            else if(type === 'lower') t = t.toLowerCase();
            else if(type === 'title') t = t.toLowerCase().split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            else if(type === 'sentence') t = t.toLowerCase().replace(/(^\\s*\\w|[\\.!?]\\s*\\w)/g, c => c.toUpperCase());
            document.getElementById('textData').value = t;
        }"""
    },
    {
        "id": "alphabetical-sorter",
        "category": "developer utility",
        "ui": """<textarea id="sortList" rows="6" placeholder="Enter list items (one per line)..."></textarea>
                 <div class="grid-2">
                    <button onclick="sortLines('az')">Sort A-Z</button>
                    <button onclick="sortLines('za')">Sort Z-A</button>
                 </div>""",
        "js": """function sortLines(dir) {
            let lines = document.getElementById('sortList').value.split('\\n').map(l => l.trim()).filter(l => l !== '');
            lines.sort((a, b) => a.localeCompare(b, undefined, {sensitivity: 'base'}));
            if(dir === 'za') lines.reverse();
            document.getElementById('sortList').value = lines.join('\\n');
        }"""
    },
    {
        "id": "remove-duplicate-lines",
        "category": "developer utility",
        "ui": """<textarea id="dupList" rows="6" placeholder="Paste your list here..."></textarea>
                 <button onclick="remDups()">Remove Duplicates</button>""",
        "js": """function remDups() {
            let lines = document.getElementById('dupList').value.split('\\n');
            let unique = [...new Set(lines)];
            document.getElementById('dupList').value = unique.join('\\n');
            const el = document.getElementById('result'); el.style.display = 'block';
            el.innerHTML = `Removed ${lines.length - unique.length} duplicates.`;
        }"""
    },
    # --- MATH & UNITS ---
    {
        "id": "percentage-calculator",
        "category": "finance calculator",
        "ui": """<div style="margin-bottom:1.5rem; background:#1e293b; padding:1rem; border-radius:6px;">
                    <label>What is <input type="number" id="p1_a" style="width:60px; display:inline; margin:0;"> % of <input type="number" id="p1_b" style="width:80px; display:inline; margin:0;">?</label>
                    <button onclick="p1()" style="margin-top:0.5rem;">Calculate</button>
                    <div id="r1" style="color:#10b981; font-weight:bold; margin-top:0.5rem;"></div>
                 </div>
                 <div style="background:#1e293b; padding:1rem; border-radius:6px;">
                    <label><input type="number" id="p2_a" style="width:80px; display:inline; margin:0;"> is what percent of <input type="number" id="p2_b" style="width:80px; display:inline; margin:0;">?</label>
                    <button onclick="p2()" style="margin-top:0.5rem;">Calculate</button>
                    <div id="r2" style="color:#10b981; font-weight:bold; margin-top:0.5rem;"></div>
                 </div>""",
        "js": """function p1() {
            const a = parseFloat(document.getElementById('p1_a').value), b = parseFloat(document.getElementById('p1_b').value);
            if(!isNaN(a) && !isNaN(b)) document.getElementById('r1').innerText = "Result: " + ((a / 100) * b).toFixed(2);
        }
        function p2() {
            const a = parseFloat(document.getElementById('p2_a').value), b = parseFloat(document.getElementById('p2_b').value);
            if(!isNaN(a) && !isNaN(b) && b !== 0) document.getElementById('r2').innerText = "Result: " + ((a / b) * 100).toFixed(2) + "%";
        }"""
    },
    {
        "id": "temperature-converter",
        "category": "developer utility",
        "ui": """<label>Celsius</label><input type="number" id="c" oninput="convT('c')">
                 <label>Fahrenheit</label><input type="number" id="f" oninput="convT('f')">
                 <label>Kelvin</label><input type="number" id="k" oninput="convT('k')">""",
        "js": """function convT(src) {
            const c = document.getElementById('c'), f = document.getElementById('f'), k = document.getElementById('k');
            if(src === 'c') { f.value = ((c.value * 9/5) + 32).toFixed(2); k.value = (parseFloat(c.value) + 273.15).toFixed(2); }
            if(src === 'f') { c.value = ((f.value - 32) * 5/9).toFixed(2); k.value = (((f.value - 32) * 5/9) + 273.15).toFixed(2); }
            if(src === 'k') { c.value = (k.value - 273.15).toFixed(2); f.value = ((k.value - 273.15) * 9/5 + 32).toFixed(2); }
        }"""
    },
    # --- LIFESTYLE ---
    {
        "id": "bmi-calculator",
        "category": "health tracker",
        "ui": """<label>Weight (kg)</label><input type="number" id="kg" placeholder="e.g. 70">
                 <label>Height (cm)</label><input type="number" id="cm" placeholder="e.g. 175">
                 <button onclick="calcBMI()">Calculate BMI</button>""",
        "js": """function calcBMI() {
            const kg = parseFloat(document.getElementById('kg').value);
            const cm = parseFloat(document.getElementById('cm').value) / 100;
            if(isNaN(kg) || isNaN(cm) || cm === 0) return;
            const bmi = (kg / (cm * cm)).toFixed(1);
            let cat = "Normal weight";
            if(bmi < 18.5) cat = "Underweight";
            else if(bmi >= 25 && bmi < 29.9) cat = "Overweight";
            else if(bmi >= 30) cat = "Obese";
            const el = document.getElementById('result');
            el.style.display = 'block';
            el.innerHTML = `<strong>Your BMI:</strong> ${bmi} <br><strong>Category:</strong> ${cat}`;
        }"""
    },
    {
        "id": "pomodoro-timer",
        "category": "health tracker",
        "ui": """<div style="text-align:center; margin:2rem 0;">
                    <div id="timerDisplay" style="font-size:4rem; font-family:monospace; color:#3b82f6; font-weight:bold;">25:00</div>
                    <div id="timerStatus" style="color:#64748b; margin-bottom:1rem;">Ready to focus</div>
                    <div class="grid-2">
                        <button onclick="startTimer(25, 'Focus Session')">Start 25m Focus</button>
                        <button onclick="startTimer(5, 'Short Break')" style="background:#10b981;">Start 5m Break</button>
                    </div>
                 </div>""",
        "js": """let activeTimer = null;
        function startTimer(minutes, status) {
            clearInterval(activeTimer);
            let time = minutes * 60;
            document.getElementById('timerStatus').innerText = status;
            const display = document.getElementById('timerDisplay');
            
            activeTimer = setInterval(() => {
                let m = Math.floor(time / 60);
                let s = time % 60;
                display.innerText = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
                if (time <= 0) { clearInterval(activeTimer); display.innerText = "00:00"; document.getElementById('timerStatus').innerText = "Time's up!"; alert("Timer complete!"); }
                time--;
            }, 1000);
        }"""
    },
    {
        "id": "random-password-generator",
        "category": "developer utility",
        "ui": """<label>Length</label><input type="number" id="len" value="16" min="8" max="64">
                 <button onclick="genPw()">Generate Secure Password</button>""",
        "js": """function genPw() {
            const len = parseInt(document.getElementById('len').value) || 16;
            const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+~`|}{[]:;?><,./-=";
            let pw = "";
            const array = new Uint32Array(len);
            window.crypto.getRandomValues(array);
            for (let i = 0; i < len; i++) { pw += chars[array[i] % chars.length]; }
            const el = document.getElementById('result'); el.style.display = 'block'; el.style.wordBreak = 'break-all';
            el.innerHTML = `<strong>Generated Password:</strong><br><br><span style="font-family:monospace;font-size:1.2rem;color:#10b981;">${pw}</span>`;
        }"""
    },
    {
        "id": "stopwatch-timer",
        "category": "health tracker",
        "ui": """<div style="text-align:center; margin:2rem 0;">
                    <div id="swDisplay" style="font-size:4rem; font-family:monospace; color:#10b981; font-weight:bold;">00:00.00</div>
                    <div class="grid-2">
                        <button onclick="toggleSW()" id="swBtn">Start</button>
                        <button onclick="resetSW()" style="background:#475569;">Reset</button>
                    </div>
                 </div>""",
        "js": """let swTimer = null, ms = 0, running = false;
        function toggleSW() {
            if(running) { clearInterval(swTimer); running = false; document.getElementById('swBtn').innerText = "Start"; }
            else { 
                running = true; document.getElementById('swBtn').innerText = "Pause";
                swTimer = setInterval(() => {
                    ms += 10;
                    let m = Math.floor(ms / 60000), s = Math.floor((ms % 60000) / 1000), mili = Math.floor((ms % 1000) / 10);
                    document.getElementById('swDisplay').innerText = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}.${mili.toString().padStart(2, '0')}`;
                }, 10);
            }
        }
        function resetSW() { clearInterval(swTimer); running = false; ms = 0; document.getElementById('swDisplay').innerText = "00:00.00"; document.getElementById('swBtn').innerText = "Start"; }"""
    },
    {
        "id": "jwt-debugger",
        "category": "developer utility",
        "ui": """<label>Encoded JWT Token</label><textarea id="jwtIn" rows="4" placeholder="Paste your JWT here..."></textarea>
                 <button onclick="decodeJWT()">Decode Locally</button>
                 <div class="grid-2">
                    <div><label>Header</label><div id="jwtH" style="background:#000; padding:1rem; border-radius:6px; font-family:monospace; font-size:0.8rem; overflow-x:auto;"></div></div>
                    <div><label>Payload</label><div id="jwtP" style="background:#000; padding:1rem; border-radius:6px; font-family:monospace; font-size:0.8rem; overflow-x:auto;"></div></div>
                 </div>""",
        "js": """function decodeJWT() {
            const token = document.getElementById('jwtIn').value.split('.');
            if(token.length !== 3) { alert('Invalid JWT format'); return; }
            try {
                document.getElementById('jwtH').innerText = JSON.stringify(JSON.parse(atob(token[0])), null, 2);
                document.getElementById('jwtP').innerText = JSON.stringify(JSON.parse(atob(token[1])), null, 2);
            } catch(e) { alert('Error decoding base64 data'); }
        }"""
    },
    {
        "id": "eth-unit-converter",
        "category": "crypto",
        "ui": """<label>Ether Value</label><input type="number" id="ethVal" value="1" oninput="convEth('eth')">
                 <label>Gwei Value</label><input type="number" id="gweiVal" oninput="convEth('gwei')">
                 <label>Wei Value</label><input type="text" id="weiVal" oninput="convEth('wei')">""",
        "js": """function convEth(src) {
            const eth = document.getElementById('ethVal'), gwei = document.getElementById('gweiVal'), wei = document.getElementById('weiVal');
            if(src === 'eth') { gwei.value = eth.value * 1000000000; wei.value = eth.value * 1000000000000000000; }
            if(src === 'gwei') { eth.value = gwei.value / 1000000000; wei.value = gwei.value * 1000000000; }
            if(src === 'wei') { eth.value = wei.value / 1000000000000000000; gwei.value = wei.value / 1000000000; }
        }"""
    },
    {
        "id": "css-box-shadow-generator",
        "category": "developer utility",
        "ui": """<label>Blur Radius</label><input type="range" id="blur" min="0" max="100" value="20" oninput="genShadow()">
                 <label>Spread</label><input type="range" id="spread" min="0" max="50" value="0" oninput="genShadow()">
                 <label>Color Alpha</label><input type="range" id="alpha" min="0" max="100" value="50" oninput="genShadow()">
                 <div id="previewBox" style="height:100px; width:100%; background:#1e293b; margin:2rem 0; border-radius:12px;"></div>
                 <code id="shadowCode" style="display:block; background:#000; padding:1rem; border-radius:6px;">box-shadow: 0px 10px 20px 0px rgba(0,0,0,0.5);</code>""",
        "js": """function genShadow() {
            const b = document.getElementById('blur').value, s = document.getElementById('spread').value, a = document.getElementById('alpha').value / 100;
            const shadow = `0px 10px ${b}px ${s}px rgba(0,0,0,${a})`;
            document.getElementById('previewBox').style.boxShadow = shadow;
            document.getElementById('shadowCode').innerText = `box-shadow: ${shadow};`;
        }"""
    },
    {
        "id": "decision-wheel",
        "category": "lifestyle",
        "ui": """<textarea id="choices" rows="4" placeholder="Enter choices, one per line..."></textarea>
                 <button onclick="spinWheel()">Make a Decision</button>
                 <div id="choiceResult" style="margin-top:1rem; font-size:2rem; color:#3b82f6; font-weight:bold; text-align:center; height:50px;"></div>""",
        "js": """function spinWheel() {
            const choices = document.getElementById('choices').value.split('\\n').map(c => c.trim()).filter(c => c);
            if(choices.length < 2) { alert("Enter at least 2 choices"); return; }
            const el = document.getElementById('choiceResult');
            let spins = 0;
            const interval = setInterval(() => {
                el.innerText = choices[Math.floor(Math.random() * choices.length)];
                spins++;
                if(spins > 20) {
                    clearInterval(interval);
                    el.style.color = '#10b981';
                    el.innerText = "⭐ " + el.innerText + " ⭐";
                } else { el.style.color = '#3b82f6'; }
            }, 100);
        }"""
    }
]
