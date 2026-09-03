/* 兽医免疫学网络课程 · 共享交互脚本
   功能：测验引擎(单选/多选/判断/开放题即时反馈)、学习进度记录、
         学习目标打卡、Tab、表单演示、年份注入。
   无任何外部依赖，全部本地完成。 */
(function () {
  "use strict";
  var NS = "vetimmuno";
  var CH = document.body.getAttribute("data-ch") || "";
  var KEY_PROG = NS + "_prog_" + CH;
  var KEY_GOAL = NS + "_goals_" + CH;
  var KEY_QUIZ = NS + "_quiz_" + CH;

  function store(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function load(k) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : null; } catch (e) { return null; } }

  /* ---------- 0. 学习页面进度（visited 记录 + 首页大进度条） ---------- */
  function trackPage() {
    var page = location.pathname.split("/").pop() || "index.html";
    if (!CH || page === "index.html") { renderProgress(); return; }
    var p = load(KEY_PROG) || { v: [] };
    if (p.v.indexOf(page) < 0) { p.v.push(page); store(KEY_PROG, p); }
    renderProgress();
  }
  function renderProgress() {
    var track = document.querySelector("[data-progress-pages]");
    var bar = document.getElementById("prog-bar");
    var num = document.getElementById("prog-num");
    if (!track) return;
    var all = (track.getAttribute("data-progress-pages") || "").split(",");
    var p = load(KEY_PROG) || { v: [] };
    var done = all.filter(function (f) { return p.v.indexOf(f) >= 0; }).length;
    var pct = all.length ? Math.round((done / all.length) * 100) : 0;
    if (bar) { bar.style.width = pct + "%"; }
    if (num) { num.textContent = done + " / " + all.length + " 页 · " + pct + "%"; }
    if (all.length && done === all.length) {
      var tip = document.getElementById("prog-tip");
      if (tip) tip.textContent = "🎉 本章核心页面已全部浏览，请完成自测与作业检验学习效果";
    }
  }

  /* ---------- 1. 学习目标打卡（goal-box） ---------- */
  function initGoals() {
    var boxes = document.querySelectorAll(".goal-box");
    if (!boxes.length) return;
    var saved = load(KEY_GOAL) || {};
    boxes.forEach(function (box) {
      var key = box.getAttribute("data-goal");
      var items = box.querySelectorAll("li");
      items.forEach(function (li, i) {
        var id = key + "_" + i;
        var done = saved[id];
        li.setAttribute("data-gid", id);
        if (done) { li.classList.add("done"); li.innerHTML = '<span class="g-t">' + li.textContent + "</span>"; }
        else if (li.getAttribute("data-raw") === null) {
          li.setAttribute("data-raw", li.textContent);
          li.innerHTML = '<span class="g-cb"></span><span class="g-t">' + li.textContent + "</span>";
        }
        li.addEventListener("click", function () {
          var gid = li.getAttribute("data-gid");
          var isDone = li.classList.toggle("done");
          saved[gid] = isDone; store(KEY_GOAL, saved);
          if (isDone) { li.innerHTML = '<span class="g-t">' + li.getAttribute("data-raw") + "</span>"; }
          else { li.innerHTML = '<span class="g-cb"></span><span class="g-t">' + li.getAttribute("data-raw") + "</span>"; }
        });
      });
      var n = box.querySelectorAll("li.done").length;
      box.setAttribute("data-done", n);
    });
  }

  /* ---------- 2. 测验引擎 ---------- */
  function answerOf(q) {
    return (q.getAttribute("data-answer") || "").toUpperCase();
  }
  function typeOf(q) { return q.getAttribute("data-type") || "single"; }
  function isJudge(q) { return typeOf(q) === "judge"; }

  function selectedVals(q) {
    var ins = q.querySelectorAll('input[type="radio"]:checked, input[type="checkbox"]:checked');
    return Array.prototype.map.call(ins, function (i) { return i.value.toUpperCase(); });
  }
  function checkQuiz(q) {
    if (!q.classList.contains("q") || q.getAttribute("data-solved")) { return; }
    var type = typeOf(q);
    var ans = answerOf(q);
    var sel = selectedVals(q);
    var fb = q.querySelector(".q-feedback");
    var explain = q.querySelector(".q-explain");
    var ref = q.querySelector(".q-ref");
    if (!fb) return;
    var ok = false;
    if (type === "open") {
      // 开放题不做自动判分，显示参考要点
      q.classList.add("solved-open");
      if (fb) { fb.className = "q-feedback show good"; }
      if (explain) { explain.style.display = "block"; }
      var vf = q.querySelector(".vf"); if (vf) vf.textContent = "已记录你的思考（开放题无标准答案）——请对照下方参考思路自查";
      return;
    }
    if (type === "single" || type === "judge") {
      ok = sel.length === 1 && sel[0] === ans;
    } else { // multi
      var want = ans.split("");
      ok = sel.length === want.length && want.every(function (w) { return sel.indexOf(w) >= 0; });
    }
    // 标色选项
    var opts = q.querySelectorAll(".q-opts label");
    opts.forEach(function (lb) {
      var v = (lb.querySelector("input").value || "").toUpperCase();
      var wantList = ans.split("");
      if (wantList.indexOf(v) >= 0) lb.classList.add("correct");
      else if (sel.indexOf(v) >= 0) lb.classList.add("wrong");
    });
    var vf = fb.querySelector(".vf");
    fb.className = "q-feedback show " + (ok ? "good" : "bad");
    if (vf) {
      if (ok && type !== "open") { vf.textContent = isJudge(q) ? "✅ 判断正确" : "✅ 回答正确！"; }
      else if (!ok && type !== "open") { vf.textContent = "❌ 再想一想——看看解析与对应知识点："; }
    }
    if (explain) { explain.style.display = "block"; }
    if (ref) { ref.style.display = "block"; }
    q.setAttribute("data-solved", "1");
    q.classList.remove("q-miss"); q.classList.remove("q-ok");
    q.classList.add(ok ? "q-ok" : "q-miss");
    countScore();
  }
  function countScore() {
    var hosts = document.querySelectorAll("[data-quiz-score]");
    if (!hosts.length) return;
    var solved = document.querySelectorAll(".q[data-solved='1']").length;
    var okN = document.querySelectorAll(".q.q-ok").length;
    var total = document.querySelectorAll('.q:not([data-count="no"])').length;
    var pct = total ? Math.round((okN / total) * 100) : 0;
    hosts.forEach(function (host) {
      var bar = host.querySelector(".progress i");
      var num = host.querySelector("#quiz-num");
      var note = host.querySelector("#quiz-note");
      if (bar) bar.style.width = pct + "%";
      if (num) num.textContent = okN + " / " + total + " 答对（" + pct + "%）";
      if (note) {
        if (solved < total) note.textContent = "已作答 " + solved + " 题，继续加油！";
        else if (pct >= 80) note.textContent = "✅ 正确率 ≥ 80%，本模块目标达成！";
        else note.textContent = "正确率未达 80%，建议复习对应模块后重做错题。";
      }
      var qz = load(KEY_QUIZ) || {};
      qz[host.getAttribute("data-quiz-score")] = { ok: okN, total: total, solved: solved };
      store(KEY_QUIZ, qz);
    });
  }
  function bindQuiz() {
    document.querySelectorAll(".quiz").forEach(function (quiz) {
      quiz.querySelectorAll(".q").forEach(function (q) {
        var btn = q.querySelector(".q-check");
        if (btn) btn.addEventListener("click", function () { checkQuiz(q); });
      });
      var all = quiz.querySelectorAll(".q-check-all");
      if (all.length) {
        all.forEach(function (b) { b.addEventListener("click", function () {
          quiz.querySelectorAll(".q").forEach(function (q) { checkQuiz(q); });
        }); });
      }
      var redo = quiz.querySelectorAll(".q-redo");
      if (redo.length) {
        redo.forEach(function (b) { b.addEventListener("click", function () {
          quiz.querySelectorAll(".q").forEach(function (q) {
            q.removeAttribute("data-solved");
            q.classList.remove("q-ok", "q-miss");
            var fb = q.querySelector(".q-feedback"); if (fb) fb.className = "q-feedback";
            var ex = q.querySelector(".q-explain"); if (ex) ex.style.display = "none";
            var rf = q.querySelector(".q-ref"); if (rf) rf.style.display = "none";
            var vf = q.querySelector(".vf"); if (vf) vf.textContent = "";
            q.querySelectorAll(".q-opts label").forEach(function (lb) {
              lb.classList.remove("correct", "wrong", "missed");
            });
            q.querySelectorAll('input').forEach(function (i) { i.checked = false; });
          });
          countScore();
        }); });
      }
    });
    countScore();
  }

  /* ---------- 3. 判断题按钮 + 隐藏 details 说明 ---------- */
  function initTabs() {
    document.querySelectorAll(".tabs").forEach(function (tabs) {
      var btns = tabs.querySelectorAll(".tab-h button");
      var ps = tabs.querySelectorAll(".tab-p");
      if (!btns.length) return;
      btns.forEach(function (b) {
        b.addEventListener("click", function () {
          btns.forEach(function (x) { x.classList.remove("active"); });
          ps.forEach(function (p) { p.classList.remove("active"); });
          b.classList.add("active");
          var idx = Array.prototype.indexOf.call(btns, b);
          if (ps[idx]) ps[idx].classList.add("active");
        });
      });
    });
  }

  /* ---------- 4. 首页/页脚二维码弹层 ---------- */
  function initQrBtn() {
    var ov = document.getElementById("qr-overlay");
    var body = document.getElementById("qr-content");
    document.querySelectorAll("[data-qr]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (ov && body) {
          body.innerHTML = btn.getAttribute("data-qr-html") ||
            '<img src="' + btn.getAttribute("data-qr") + '" alt="二维码" style="width:240px;height:240px;border-radius:8px">';
          ov.classList.add("show");
        }
      });
    });
    if (ov) ov.addEventListener("click", function (e) {
      if (e.target === ov || e.target.classList.contains("ov-close")) ov.classList.remove("show");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && ov && ov.classList.contains("show")) ov.classList.remove("show");
    });
  }

  /* ---------- 5. 作业提交（演示：本地校验+清单生成） ---------- */
  function initHomework() {
    var form = document.getElementById("hw-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = (document.getElementById("hw-name") || {}).value || "同学";
      var res = document.getElementById("hw-result");
      if (res) {
        res.classList.add("show");
        var lines = [];
        form.querySelectorAll("input[type=text],textarea").forEach(function (i) { if (i.value.trim()) lines.push(i.value.trim().slice(0, 60)); });
        var n = document.querySelectorAll("#hw-checklist input:checked").length || 0;
        document.getElementById("hw-echo").textContent =
          name + "，你已选择完成 " + n + " 项作业，并填写 " + lines.length + " 项内容。请拍照/导出后交任课教师或上传学习平台。";
      }
      var btn = form.querySelector('button[type="submit"]');
      if (btn) btn.disabled = true;
    });
  }

  /* ---------- 6. 快速反馈问卷 ---------- */
  function initFeedback() {
    var form = document.getElementById("fb-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var res = document.getElementById("fb-result");
      if (res) res.classList.add("show");
    });
  }

  /* ---------- 7. 目录锚点点击进度跳转平滑 ---------- */
  function smooth() {
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener("click", function () { /* 交给CSS smooth scroll */ });
    });
  }

  /* ---------- 8. 回到顶部 ---------- */
  function backTop() {
    var b = document.getElementById("back-top");
    if (!b) return;
    var show = function () { b.style.display = window.scrollY > 500 ? "block" : "none"; };
    window.addEventListener("scroll", show); show();
    b.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  }

  /* ---------- 启动 ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    trackPage(); initGoals(); bindQuiz(); initTabs();
    initQrBtn(); initHomework(); initFeedback(); backTop();
    // 年份
    var y = document.getElementById("year");
    if (y) y.textContent = new Date().getFullYear();
  });
})();
