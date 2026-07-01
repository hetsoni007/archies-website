/* =========================================================================
   Aarchi's — "style quiz" lead capture -> WhatsApp (no backend).
   A tappable multi-step flow that ends by opening WhatsApp pre-filled.
   Fires GA4 events (quiz_start / quiz_step / quiz_complete / generate_lead).
   Renders into #style-quiz. Depends on nothing.
   ========================================================================= */
(function () {
  var WA = "919879390731";
  var mount = document.getElementById("style-quiz");
  if (!mount) return;

  var STEPS = [
    { key: "occasion", q: "What are you dressing for?",
      opts: ["Wedding", "Reception", "Sangeet / Mehndi", "Festive / Navratri", "Baby shower", "Everyday / Other"] },
    { key: "piece", q: "What piece do you have in mind?",
      opts: ["Bridal lehenga", "Saree", "Anarkali / Gown", "Men's ethnic", "Baby-shower outfit", "Not sure yet"] },
    { key: "timeline", q: "When do you need it by?",
      opts: ["Within a month", "1–3 months", "3–6 months", "Just exploring"] },
    { key: "location", q: "Where should we deliver? (we ship worldwide)",
      opts: ["India", "USA", "UK", "Elsewhere"] }
  ];
  var answers = {}, step = 0, started = false;
  var TOTAL = STEPS.length + 1;

  function ev(n, p) { try { if (window.track) track(n, p); else if (window.gtag) gtag("event", n, p || {}); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function head(n) {
    return '<div class="quiz-head"><span class="quiz-step">Step ' + (n + 1) + ' of ' + TOTAL + '</span>'
      + '<div class="quiz-bar"><i style="width:' + (n / TOTAL * 100) + '%"></i></div></div>';
  }

  function render() {
    if (step < STEPS.length) {
      var s = STEPS[step];
      mount.innerHTML = head(step)
        + '<h3 class="quiz-q">' + s.q + '</h3>'
        + '<div class="quiz-opts">' + s.opts.map(function (o) {
            return '<button type="button" class="quiz-opt' + (answers[s.key] === o ? " sel" : "") + '" data-val="' + esc(o) + '">' + esc(o) + "</button>";
          }).join("") + "</div>"
        + (step > 0 ? '<button type="button" class="quiz-back">&larr; Back</button>' : "");
      mount.querySelectorAll(".quiz-opt").forEach(function (b) {
        b.addEventListener("click", function () {
          answers[s.key] = b.dataset.val;
          if (!started) { started = true; ev("quiz_start", {}); }
          ev("quiz_step", { step: step + 1, question: s.key, answer: b.dataset.val });
          step++; render();
        });
      });
      var back = mount.querySelector(".quiz-back");
      if (back) back.addEventListener("click", function () { step--; render(); });
    } else {
      mount.innerHTML = head(STEPS.length)
        + '<h3 class="quiz-q">Lovely — and your name?</h3>'
        + '<div class="quiz-summary">' + STEPS.map(function (s) { return "<span>" + esc(answers[s.key]) + "</span>"; }).join("") + "</div>"
        + '<input class="quiz-name" id="quiz-name" placeholder="Your name" autocomplete="name" maxlength="60">'
        + '<button type="button" class="btn btn-primary quiz-go" id="quiz-go">Send my enquiry on WhatsApp</button>'
        + '<button type="button" class="quiz-back">&larr; Back</button>';
      mount.querySelector(".quiz-back").addEventListener("click", function () { step--; render(); });
      mount.querySelector("#quiz-go").addEventListener("click", submit);
      var ni = mount.querySelector("#quiz-name");
      ni.addEventListener("keydown", function (e) { if (e.key === "Enter") submit(); });
      ni.focus();
    }
  }

  function submit() {
    var name = (mount.querySelector("#quiz-name") || {}).value || "";
    ev("quiz_complete", { occasion: answers.occasion, piece: answers.piece, timeline: answers.timeline, deliver_to: answers.location });
    ev("generate_lead", { value: 1, currency: "INR" });
    var msg = "Hi Aarchi's! I'd love to enquire ✨\n"
      + "• Occasion: " + (answers.occasion || "-") + "\n"
      + "• Piece: " + (answers.piece || "-") + "\n"
      + "• Timeline: " + (answers.timeline || "-") + "\n"
      + "• Deliver to: " + (answers.location || "-") + "\n"
      + (name ? "• Name: " + name + "\n" : "")
      + "\n(via aarchisbyarchanasoni.com)";
    window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(msg), "_blank", "noopener");
    mount.innerHTML = '<div class="quiz-done"><h3>Opening WhatsApp…</h3>'
      + '<p>If it didn’t open, <a href="https://wa.me/' + WA + '">tap here to message us</a> — we’ll reply with ideas &amp; a quote.</p></div>';
  }

  render();
})();
