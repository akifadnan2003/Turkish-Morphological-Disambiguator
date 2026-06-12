"""
Generate PDF project report for Turkish Morphological Disambiguation.
BTU - Dogal Dil Isleme | 2025-2026 Bahar Donemi

Run: python -X utf8 generate_report.py
Output: report/NLP_Project_Report_AkifAdnan.pdf
"""

import os
import matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Paths ─────────────────────────────────────────────────
BASE    = os.path.dirname(os.path.abspath(__file__))
RES     = os.path.join(BASE, "results")
OUT_DIR = os.path.join(BASE, "report")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PDF = os.path.join(OUT_DIR, "NLP_Project_Report_AkifAdnan.pdf")

# ── Student info ───────────────────────────────────────────
STUDENT_NAME   = "Akif Adnan"
STUDENT_NO     = "20360859106"
UNIVERSITY     = "T.C. Bursa Teknik Universitesi"
FACULTY        = "Muhendislik ve Doga Bilimleri Fakultesi"
DEPARTMENT     = "Bilgisayar Muhendisligi Bolumu"
COURSE         = "Dogal Dil Isleme (Natural Language Processing)"
SEMESTER       = "2025 - 2026 Bahar Donemi"
PROJECT_TITLE  = "Turkish Morphological Disambiguation"
PROJECT_TOPIC  = "Proje 1 - Morofolojik Cozumleme"
DATE           = "Haziran 2026"

# ── Font registration (DejaVu from matplotlib — supports Turkish) ──
_mpl_fonts = os.path.join(os.path.dirname(matplotlib.__file__),
                           "mpl-data", "fonts", "ttf")
_font_map = {
    "DejaVu":       "DejaVuSans.ttf",
    "DejaVuBold":   "DejaVuSans-Bold.ttf",
    "DejaVuItalic": "DejaVuSans-Oblique.ttf",
}
for _name, _file in _font_map.items():
    _path = os.path.join(_mpl_fonts, _file)
    if os.path.exists(_path):
        pdfmetrics.registerFont(TTFont(_name, _path))

# ── Color palette ──────────────────────────────────────────
NAVY    = colors.HexColor("#1d4ed8")
DKBLUE  = colors.HexColor("#1e3a5f")
STEEL   = colors.HexColor("#475569")
LGRAY   = colors.HexColor("#f1f5f9")
MGRAY   = colors.HexColor("#e2e8f0")
GREEN   = colors.HexColor("#15803d")
AMBER   = colors.HexColor("#92400e")
WHITE   = colors.white
BLACK   = colors.HexColor("#0f172a")

# ── Styles ─────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

styles = {
    "cover_uni":    S("cu",  fontName="DejaVuBold",   fontSize=11, textColor=WHITE,   alignment=TA_CENTER, leading=16),
    "cover_title":  S("ct",  fontName="DejaVuBold",   fontSize=20, textColor=WHITE,   alignment=TA_CENTER, leading=26, spaceAfter=6),
    "cover_sub":    S("cs",  fontName="DejaVu",        fontSize=12, textColor=LGRAY,  alignment=TA_CENTER, leading=18),
    "cover_info":   S("ci",  fontName="DejaVu",        fontSize=10, textColor=LGRAY,  alignment=TA_CENTER, leading=15),
    "h1":           S("h1",  fontName="DejaVuBold",   fontSize=14, textColor=NAVY,    spaceBefore=18, spaceAfter=6,  leading=18),
    "h2":           S("h2",  fontName="DejaVuBold",   fontSize=11, textColor=DKBLUE,  spaceBefore=12, spaceAfter=4,  leading=15),
    "body":         S("b",   fontName="DejaVu",        fontSize=9.5,textColor=BLACK,   alignment=TA_JUSTIFY, leading=15, spaceAfter=4),
    "bullet":       S("bl",  fontName="DejaVu",        fontSize=9.5,textColor=BLACK,   leftIndent=14, leading=14, spaceAfter=2),
    "caption":      S("cap", fontName="DejaVuItalic",  fontSize=8.5,textColor=STEEL,   alignment=TA_CENTER, spaceBefore=4, spaceAfter=10),
    "mono":         S("mo",  fontName="DejaVu",        fontSize=8,  textColor=BLACK,   leading=12),
    "footer":       S("ft",  fontName="DejaVu",        fontSize=8,  textColor=STEEL,   alignment=TA_RIGHT),
    "tblhdr":       S("th",  fontName="DejaVuBold",   fontSize=8.5,textColor=WHITE,   alignment=TA_CENTER),
    "tblcell":      S("tc",  fontName="DejaVu",        fontSize=8.5,textColor=BLACK,   alignment=TA_LEFT,  leading=12),
    "tblcellc":     S("tcc", fontName="DejaVu",        fontSize=8.5,textColor=BLACK,   alignment=TA_CENTER,leading=12),
    "note":         S("nt",  fontName="DejaVuItalic",  fontSize=8.5,textColor=STEEL,   alignment=TA_LEFT, spaceBefore=4),
}

P  = lambda txt, sty="body": Paragraph(txt, styles[sty])
SP = lambda n=6: Spacer(1, n)
HR = lambda: HRFlowable(width="100%", thickness=0.5, color=MGRAY, spaceAfter=8, spaceBefore=4)

# ── Table helpers ──────────────────────────────────────────
HDR_STYLE = [
    ("BACKGROUND",  (0,0), (-1,0), NAVY),
    ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
    ("FONTNAME",    (0,0), (-1,0), "DejaVuBold"),
    ("FONTSIZE",    (0,0), (-1,-1), 8.5),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
    ("GRID",        (0,0), (-1,-1), 0.4, MGRAY),
    ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",  (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
]

def make_table(data, col_widths, extra_styles=None):
    ts = TableStyle(HDR_STYLE + (extra_styles or []))
    return Table(data, colWidths=col_widths, style=ts, repeatRows=1)

# ── Page size ──────────────────────────────────────────────
W, H = A4   # 595.27 x 841.89 pts
ML = MR = 2*cm
MT = MB = 2.5*cm
TW = W - ML - MR   # usable text width

# ── Page callbacks ─────────────────────────────────────────
def on_first_page(canvas, doc):
    """Full navy background on cover page."""
    canvas.saveState()
    canvas.setFillColor(DKBLUE)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.restoreState()

def on_later_pages(canvas, doc):
    """Footer on all pages after the cover."""
    canvas.saveState()
    canvas.setFont("DejaVu", 8)
    canvas.setFillColor(STEEL)
    canvas.setStrokeColor(MGRAY)
    canvas.setLineWidth(0.5)
    canvas.line(ML, MB - 0.3*cm, W - MR, MB - 0.3*cm)
    canvas.drawString(ML, MB - 0.7*cm,
                      f"{STUDENT_NAME}  |  {STUDENT_NO}  |  {COURSE}")
    canvas.drawRightString(W - MR, MB - 0.7*cm, f"Page {doc.page - 1}")
    canvas.restoreState()

# ── Image helper ───────────────────────────────────────────
def embed_image(filename, max_width=TW, max_height=14*cm):
    path = os.path.join(RES, filename)
    if not os.path.exists(path):
        return P(f"[Image not found: {filename}]", "note")
    img = RLImage(path)
    iw, ih = img.imageWidth, img.imageHeight
    scale = min(max_width / iw, max_height / ih, 1.0)
    img.drawWidth  = iw * scale
    img.drawHeight = ih * scale
    return img

# ══════════════════════════════════════════════════════════
# CONTENT
# ══════════════════════════════════════════════════════════
story = []

# ─────────────────────────────────────────────────────────
# COVER PAGE  (navy background drawn by on_first_page)
# ─────────────────────────────────────────────────────────
story += [
    SP(60),
    P(UNIVERSITY,   "cover_uni"),
    P(FACULTY,      "cover_uni"),
    P(DEPARTMENT,   "cover_uni"),
    SP(8),
    HRFlowable(width="60%", thickness=1, color=colors.HexColor("#93c5fd"),
               hAlign="CENTER", spaceAfter=16, spaceBefore=8),
    P(COURSE,       "cover_sub"),
    P(SEMESTER,     "cover_sub"),
    SP(40),
    P(PROJECT_TOPIC,"cover_sub"),
    SP(10),
    P(PROJECT_TITLE,"cover_title"),
    SP(40),
    HRFlowable(width="40%", thickness=0.8, color=colors.HexColor("#93c5fd"),
               hAlign="CENTER", spaceAfter=20, spaceBefore=4),
    P(STUDENT_NAME,            "cover_info"),
    P(f"Student No: {STUDENT_NO}", "cover_info"),
    P("Individual Submission",     "cover_info"),
    SP(16),
    P(DATE,                        "cover_info"),
    PageBreak(),
]

# ─────────────────────────────────────────────────────────
# SECTION 1 — INTRODUCTION
# ─────────────────────────────────────────────────────────
story += [
    P("1. Introduction", "h1"), HR(),
    P("Morphological disambiguation is the task of assigning the correct "
      "grammatical analysis to each word in a sentence when multiple analyses "
      "are possible. This project addresses this problem for Turkish, which is "
      "an <b>agglutinative language</b> — words are formed by attaching "
      "suffixes to roots, allowing a single surface form to carry many possible "
      "morphological readings.", "body"),
    SP(6),
    P("<b>Why Turkish is challenging.</b> Consider the word <i>guzel</i>: "
      "it can function as an adjective (beautiful), a noun (beauty), or an "
      "adverb (beautifully) depending on context. The same surface form is "
      "grammatically ambiguous without the surrounding sentence. This ambiguity "
      "must be resolved before any higher-level NLP task (translation, parsing, "
      "question answering) can be performed reliably.", "body"),
    SP(6),
    P("<b>Project objective.</b> Train a statistical machine learning model "
      "(Conditional Random Fields) on the UD Turkish-IMST Treebank to "
      "automatically predict the correct Universal Part-of-Speech (UPOS) tag "
      "for each token in a given Turkish sentence. Evaluate the model on a "
      "held-out test set and on 25 manually annotated sentences.", "body"),
    SP(10),
    P("2. Dataset", "h1"), HR(),
    P("<b>UD Turkish-IMST Treebank.</b> The Universal Dependencies (UD) "
      "project provides standardized annotated corpora across 100+ languages. "
      "The Turkish IMST treebank was created at Istanbul Technical University "
      "and contains sentences manually annotated by linguists in CoNLL-U format.", "body"),
    SP(6),
]

# Data splits table
data_table = make_table(
    [
        [P("Split","tblhdr"), P("Sentences","tblhdr"), P("Tokens","tblhdr"), P("Purpose","tblhdr")],
        [P("Train","tblcell"), P("3,435","tblcellc"), P("~52,000","tblcellc"), P("Model training","tblcell")],
        [P("Dev","tblcell"),   P("1,100","tblcellc"), P("~17,000","tblcellc"), P("Hyperparameter tuning","tblcell")],
        [P("Test","tblcell"),  P("1,100","tblcellc"), P("~10,000","tblcellc"), P("Final evaluation","tblcell")],
        [P("Manual (custom)","tblcell"), P("25","tblcellc"), P("169","tblcellc"), P("Hand-annotated by student","tblcell")],
    ],
    [TW*0.15, TW*0.2, TW*0.2, TW*0.45]
)
story += [data_table, P("Table 1. Dataset splits used in this project.", "caption"), SP(6)]

story += [
    P("<b>CoNLL-U Format.</b> Every sentence is stored in a tab-separated "
      "file where each row represents one token. The key columns are: "
      "ID (position), FORM (surface word), LEMMA (root), UPOS (universal "
      "POS tag — the label we predict), and FEATS (morphological features "
      "such as Case, Number, Tense, Person).", "body"),
    SP(6),
    P("Sample annotation:", "body"),
]

conllu_data = make_table(
    [
        [P("ID","tblhdr"), P("FORM","tblhdr"), P("LEMMA","tblhdr"), P("UPOS","tblhdr"), P("FEATS","tblhdr")],
        [P("1","tblcellc"), P("Ogrenciler","tblcell"), P("ogrenci","tblcell"), P("NOUN","tblcellc"), P("Case=Nom|Number=Plur","tblcell")],
        [P("2","tblcellc"), P("bugun","tblcell"),      P("bugun","tblcell"),   P("ADV","tblcellc"),  P("_","tblcellc")],
        [P("3","tblcellc"), P("sinava","tblcell"),     P("sinav","tblcell"),   P("NOUN","tblcellc"), P("Case=Dat|Number=Sing","tblcell")],
        [P("4","tblcellc"), P("calisiyor","tblcell"),  P("calis","tblcell"),   P("VERB","tblcellc"), P("Mood=Ind|Tense=Pres|Person=3","tblcell")],
        [P("5","tblcellc"), P(".","tblcell"),          P(".","tblcell"),       P("PUNCT","tblcellc"),P("_","tblcellc")],
    ],
    [TW*0.07, TW*0.2, TW*0.18, TW*0.12, TW*0.43]
)
story += [conllu_data, P('Table 2. CoNLL-U annotation example: "Ogrenciler bugun sinava calisiyor."', "caption")]
story.append(PageBreak())

# ─────────────────────────────────────────────────────────
# SECTION 3 — METHODOLOGY
# ─────────────────────────────────────────────────────────
story += [
    P("3. Methodology", "h1"), HR(),
    P("<b>3.1 Algorithm: Conditional Random Fields (CRF)</b>", "h2"),
    P("A Conditional Random Field is a discriminative sequence labeling model. "
      "Unlike a simple per-token classifier, a CRF labels the entire sentence "
      "jointly — it learns transition probabilities between adjacent labels "
      "(e.g., DET is almost always followed by NOUN or ADJ). "
      "This is critical for Turkish where word order encodes strong contextual "
      "signals about neighbouring POS categories.", "body"),
    SP(6),
    P("The model optimizes:", "body"),
    P("P(y1, y2, ..., yn | x1, x2, ..., xn)  — the probability of the entire "
      "label sequence given the word sequence — using L-BFGS optimization "
      "with L1 regularization (c1=0.05) and L2 regularization (c2=0.05).", "mono"),
    SP(8),
    P("<b>3.2 Feature Engineering</b>", "h2"),
    P("The following features were hand-designed specifically for Turkish "
      "morphology. Each feature is computed per token and fed into the CRF:", "body"),
    SP(4),
]

feat_table = make_table(
    [
        [P("Feature","tblhdr"), P("Examples","tblhdr"), P("Signal","tblhdr")],
        [P("Word suffixes (last 2-4 chars)","tblcell"), P("-dan/-den, -da/-de","tblcell"),    P("Ablative/Locative -> NOUN","tblcell")],
        [P("Tense suffix","tblcell"),                   P("-yor/-iyor, -di/-du","tblcell"),   P("Present/Past -> VERB","tblcell")],
        [P("Plural suffix","tblcell"),                  P("-lar/-ler","tblcell"),              P("NOUN","tblcell")],
        [P("Infinitive suffix","tblcell"),              P("-mak/-mek","tblcell"),              P("VERB (verbal noun)","tblcell")],
        [P("Adj-forming suffix","tblcell"),             P("-li/-lu, -siz/-suz","tblcell"),     P("ADJ","tblcell")],
        [P("Evidential suffix","tblcell"),              P("-mis/-mush","tblcell"),             P("VERB","tblcell")],
        [P("Vowel harmony","tblcell"),                  P("front/back last vowel","tblcell"),  P("Morphological class","tblcell")],
        [P("Context window +-2","tblcell"),             P("prev/next 2 words","tblcell"),      P("Disambiguation by context","tblcell")],
        [P("Capitalization","tblcell"),                 P("Starts with uppercase","tblcell"),  P("PROPN signal","tblcell")],
        [P("Contains apostrophe","tblcell"),            P("Ankara'da","tblcell"),              P("PROPN (proper noun + suffix)","tblcell")],
        [P("Is digit / has digit","tblcell"),           P("2024, 3.5","tblcell"),              P("NUM","tblcell")],
    ],
    [TW*0.35, TW*0.3, TW*0.35]
)
story += [feat_table, P("Table 3. Turkish-specific features used in the CRF model (40+ total).", "caption")]
story.append(SP(10))

story += [
    P("<b>3.3 Zemberek ve Aday Çözümleme Yaklaşımı (Candidate Generation)</b>", "h2"),
    P("Proje isterlerinde belirtilen Zemberek tabanlı aday kelime çözümleme mantığı, "
      "sistemde <i>Corpus-Based Candidate Dictionary</i> (Derlem Tabanlı Aday Sözlüğü) "
      "yöntemiyle simüle edilmiştir. Java tabanlı Zemberek kütüphanesinin Python "
      "ortamında yaratabileceği bağımlılık ve gRPC köprüsü sorunlarını aşmak adına, "
      "eğitim veri setinde (UD_Turkish-IMST) geçen her kelimenin aldığı tüm olası "
      "morfolojik etiketler bir sözlükte toplanmıştır.", "body"),
    SP(6),
    P("<b>candidate_disambig.py</b> dosyasında görülebileceği üzere, sisteme verilen "
      "bir cümlenin her kelimesi için önce bu olası aday listesi (candidate list) "
      "çekilmekte, ardından CRF modelinin marjinal olasılıkları "
      "(<i>predict_marginals</i>) kullanılarak bu adaylar arasında en yüksek "
      "olasılıklı olanı seçilerek 'Disambiguation' (Çözümleme) işlemi "
      "tamamlanmaktadır.", "body"),
    SP(6),
    P("<b>İki Aşamalı Morfolojik Pipeline (Two-Stage Pipeline)</b>", "h2"),
    P("Morfolojik özellik (FEATS) tahmini için iki aşamalı bir mimari "
      "benimsenmiştir:", "body"),
    P("• <b>Aşama 1 — CRF:</b> Model, bağlam penceresindeki özellikler "
      "kullanılarak her belirteç için UPOS etiketini tahmin eder (%90,93 doğruluk).", "bullet"),
    P("• <b>Aşama 2 — Derlem Sözlüğü:</b> Tahmin edilen (kelime, UPOS) çifti için "
      "eğitim verisindeki en sık görülen FEATS kombinasyonu atanır. Bu adım, "
      "Zemberek'in sağlayacağı morfolojik aday analizlerini simüle etmektedir.", "bullet"),
    SP(4),
    P("Bu mimari tercih, 985 benzersiz UPOS+FEATS kombinasyonunu tek bir CRF "
      "modeliyle öğretmeye çalışmanın (sınıf patlaması problemi) önüne geçerek "
      "akademik literatürde yaygın olan pipeline yaklaşımını uygulamaktadır.", "body"),
]
story.append(PageBreak())

# ─────────────────────────────────────────────────────────
# SECTION 4 — MANUAL ANNOTATIONS
# ─────────────────────────────────────────────────────────
story += [
    P("4. Manual Annotations", "h1"), HR(),
    P("To demonstrate understanding of the annotation task and to evaluate "
      "the model on fully independent data, 25 Turkish sentences were manually "
      "annotated in CoNLL-U format. These sentences were chosen to cover diverse "
      "syntactic structures and domains, and were not drawn from the treebank.", "body"),
    SP(6),
]

domain_table = make_table(
    [
        [P("Domain","tblhdr"), P("Sentences","tblhdr"), P("Example","tblhdr")],
        [P("University / Academic","tblcell"),  P("8","tblcellc"), P("Proje odevini yarin teslim etmelisin .","tblcell")],
        [P("Daily Life","tblcell"),             P("8","tblcellc"), P("Kardesim bu hafta Izmir'den gelecek .","tblcell")],
        [P("NLP / Technology","tblcell"),       P("5","tblcellc"), P("CRF modeli Turkce icin basarili sonuclar verdi .","tblcell")],
        [P("Geography","tblcell"),              P("2","tblcellc"), P("Turkiye'nin baskenti Ankara'dir .","tblcell")],
        [P("Nature","tblcell"),                 P("1","tblcellc"), P("Daglarda kar yagiyordu ve hava cok soguktu .","tblcell")],
        [P("NLP Evaluation","tblcell"),         P("1","tblcellc"), P("Modelin basari orani yuzde doksana ulasti .","tblcell")],
        [P("<b>Total</b>","tblcell"),           P("<b>25</b>","tblcellc"), P("169 tokens","tblcell")],
    ],
    [TW*0.3, TW*0.15, TW*0.55]
)
story += [domain_table, P("Table 4. Manual annotation set by domain.", "caption"), SP(8)]

story += [
    P("<b>Annotation scheme.</b> Each token was annotated with:", "body"),
    P("• <b>UPOS</b> — Universal Part-of-Speech tag (13 classes)", "bullet"),
    P("• <b>Lemma</b> — dictionary root form", "bullet"),
    P("• <b>FEATS</b> — morphological features: Case, Number, Person, Tense, "
      "Mood, Polarity, VerbForm, Voice, Poss", "bullet"),
    SP(8),
    P("Linguistically interesting constructions annotated include:", "body"),
    P("• <b>Converbs</b> (VerbForm=Conv): e.g., <i>kalkip</i> — links two verbal events", "bullet"),
    P("• <b>Verbal nouns</b> (VerbForm=Vnoun): e.g., <i>ogrenmesi</i>, <i>olmay</i>", "bullet"),
    P("• <b>Passive voice</b> (Voice=Pass): e.g., <i>gelistirilmistir</i>, <i>yapilmistir</i>", "bullet"),
    P("• <b>Negative polarity</b> (Polarity=Neg): e.g., <i>cikamadim</i>", "bullet"),
    P("• <b>Necessity mood</b> (Mood=Nec): e.g., <i>etmelisin</i>", "bullet"),
]
story.append(PageBreak())

# ─────────────────────────────────────────────────────────
# SECTION 5 — RESULTS
# ─────────────────────────────────────────────────────────
story += [
    P("5. Results", "h1"), HR(),
    P("<b>5.1 Treebank Test Set (1,100 sentences, 10,032 tokens)</b>", "h2"),
    P("The trained CRF model was evaluated on the held-out test split of the "
      "UD Turkish-IMST treebank. The following table reports per-class "
      "precision, recall, F1-score and support (number of instances).", "body"),
    SP(6),
]

results_table = make_table(
    [
        [P("UPOS Tag","tblhdr"), P("Precision","tblhdr"), P("Recall","tblhdr"),
         P("F1-Score","tblhdr"), P("Support","tblhdr")],
        [P("PUNCT","tblcell"),  P("0.9990","tblcellc"), P("1.0000","tblcellc"), P("0.9995","tblcellc"), P("1,933","tblcellc")],
        [P("AUX","tblcell"),    P("0.9442","tblcellc"), P("0.9621","tblcellc"), P("0.9531","tblcellc"), P("211","tblcellc")],
        [P("VERB","tblcell"),   P("0.9375","tblcellc"), P("0.9409","tblcellc"), P("0.9392","tblcellc"), P("1,928","tblcellc")],
        [P("CCONJ","tblcell"),  P("0.9635","tblcellc"), P("0.9635","tblcellc"), P("0.9635","tblcellc"), P("356","tblcellc")],
        [P("PRON","tblcell"),   P("0.9452","tblcellc"), P("0.9289","tblcellc"), P("0.9370","tblcellc"), P("464","tblcellc")],
        [P("ADP","tblcell"),    P("0.9556","tblcellc"), P("0.9048","tblcellc"), P("0.9295","tblcellc"), P("357","tblcellc")],
        [P("DET","tblcell"),    P("0.8422","tblcellc"), P("0.9622","tblcellc"), P("0.8982","tblcellc"), P("344","tblcellc")],
        [P("NOUN","tblcell"),   P("0.8432","tblcellc"), P("0.9251","tblcellc"), P("0.8823","tblcellc"), P("2,430","tblcellc")],
        [P("ADV","tblcell"),    P("0.8875","tblcellc"), P("0.7701","tblcellc"), P("0.8246","tblcellc"), P("461","tblcellc")],
        [P("NUM","tblcell"),    P("0.9073","tblcellc"), P("0.7135","tblcellc"), P("0.7988","tblcellc"), P("192","tblcellc")],
        [P("ADJ","tblcell"),    P("0.8485","tblcellc"), P("0.7583","tblcellc"), P("0.8009","tblcellc"), P("960","tblcellc")],
        [P("PROPN","tblcell"),  P("0.8333","tblcellc"), P("0.7086","tblcellc"), P("0.7659","tblcellc"), P("374","tblcellc")],
        [P("<b>Accuracy</b>","tblcell"), P("","tblcellc"), P("","tblcellc"),
         P("<b>0.9093</b>","tblcellc"), P("<b>10,032</b>","tblcellc")],
        [P("<b>Weighted avg</b>","tblcell"), P("<b>0.9099</b>","tblcellc"),
         P("<b>0.9093</b>","tblcellc"), P("<b>0.9080</b>","tblcellc"), P("10,032","tblcellc")],
    ],
    [TW*0.18, TW*0.2, TW*0.18, TW*0.2, TW*0.24],
    extra_styles=[
        ("BACKGROUND", (0,13), (-1,13), colors.HexColor("#dbeafe")),
        ("BACKGROUND", (0,14), (-1,14), colors.HexColor("#dbeafe")),
    ]
)
story += [results_table, P("Table 5. Per-class evaluation results on the treebank test set.", "caption")]
story.append(PageBreak())

# ─────────────────────────────────────────────────────────
# SECTION 5.2 — F1 BAR CHART
# ─────────────────────────────────────────────────────────
story += [
    P("<b>5.2 F1 Score per Class</b>", "h2"),
    P("The bar chart below visualises the F1-score for each UPOS class on the "
      "test set. Classes with distinctive morphological markers (PUNCT, AUX, "
      "VERB, CCONJ) achieve near-perfect scores. The hardest classes are PROPN "
      "and ADJ where surface form overlap with other categories causes errors.", "body"),
    SP(8),
    embed_image("f1_per_class_test.png", max_height=11*cm),
    P("Figure 1. F1 score per UPOS class on the treebank test set.", "caption"),
]
story.append(PageBreak())

# ─────────────────────────────────────────────────────────
# SECTION 5.3 — CONFUSION MATRIX
# ─────────────────────────────────────────────────────────
story += [
    P("<b>5.3 Confusion Matrix</b>", "h2"),
    P("The confusion matrix shows true labels (rows) against predicted labels "
      "(columns). The diagonal represents correct predictions. "
      "Key error patterns: PROPN is frequently predicted as NOUN (proper nouns "
      "lack distinctive suffixes when unseen), and ADJ is confused with NOUN "
      "(Turkish adjectives and nouns share identical surface forms in many "
      "constructions).", "body"),
    SP(8),
    embed_image("confusion_matrix_test.png", max_height=13*cm),
    P("Figure 2. Confusion matrix on the treebank test set. "
      "Diagonal = correct predictions. Rows = true label, Columns = predicted label.", "caption"),
]
story.append(PageBreak())

# ─────────────────────────────────────────────────────────
# SECTION 6 — CUSTOM EVALUATION
# ─────────────────────────────────────────────────────────
story += [
    P("6. Evaluation on Manual Annotations", "h1"), HR(),
    P("The trained model was also evaluated on the 25 manually annotated "
      "sentences (169 tokens) in <i>my_annotations.conllu</i>. This set was "
      "created independently and was never seen during training, providing an "
      "additional out-of-domain evaluation.", "body"),
    SP(6),
]

custom_table = make_table(
    [
        [P("UPOS Tag","tblhdr"), P("Precision","tblhdr"), P("Recall","tblhdr"),
         P("F1-Score","tblhdr"), P("Support","tblhdr")],
        [P("ADJ","tblcell"),   P("0.6364","tblcellc"), P("0.7778","tblcellc"), P("0.7000","tblcellc"), P("18","tblcellc")],
        [P("ADP","tblcell"),   P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("2","tblcellc")],
        [P("ADV","tblcell"),   P("1.0000","tblcellc"), P("0.4615","tblcellc"), P("0.6316","tblcellc"), P("13","tblcellc")],
        [P("CCONJ","tblcell"), P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("1","tblcellc")],
        [P("DET","tblcell"),   P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("11","tblcellc")],
        [P("NOUN","tblcell"),  P("0.8571","tblcellc"), P("0.8276","tblcellc"), P("0.8421","tblcellc"), P("58","tblcellc")],
        [P("NUM","tblcell"),   P("0.7500","tblcellc"), P("1.0000","tblcellc"), P("0.8571","tblcellc"), P("3","tblcellc")],
        [P("PRON","tblcell"),  P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("2","tblcellc")],
        [P("PROPN","tblcell"), P("0.7500","tblcellc"), P("1.0000","tblcellc"), P("0.8571","tblcellc"), P("6","tblcellc")],
        [P("PUNCT","tblcell"), P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("1.0000","tblcellc"), P("25","tblcellc")],
        [P("VERB","tblcell"),  P("0.9375","tblcellc"), P("1.0000","tblcellc"), P("0.9677","tblcellc"), P("30","tblcellc")],
        [P("<b>Accuracy</b>","tblcell"), P("","tblcellc"), P("","tblcellc"),
         P("<b>0.8757</b>","tblcellc"), P("<b>169</b>","tblcellc")],
    ],
    [TW*0.18, TW*0.2, TW*0.18, TW*0.2, TW*0.24],
    extra_styles=[
        ("BACKGROUND", (0,12), (-1,12), colors.HexColor("#dbeafe")),
    ]
)
story += [custom_table, P("Table 6. Per-class evaluation results on the 25 manually annotated sentences.", "caption"), SP(8)]

story += [
    P("The model achieves <b>87.57% accuracy</b> on the custom set, "
      "confirming that it generalises beyond the training data. "
      "The drop from 90.93% (treebank) to 87.57% (custom) is expected — "
      "the custom sentences contain more complex structures (converbs, "
      "verbal nouns, passive voice) and informal vocabulary.", "body"),
]
story.append(PageBreak())

# ─────────────────────────────────────────────────────────
# SECTION 7 — ERROR ANALYSIS
# ─────────────────────────────────────────────────────────
story += [
    P("7. Error Analysis", "h1"), HR(),
    P("Analysis of misclassified tokens reveals three systematic error patterns:", "body"),
    SP(6),
    P("<b>7.1 ADV confused with NOUN</b>", "h2"),
    P("Short temporal adverbs such as <i>dun</i> (yesterday), <i>bugun</i> "
      "(today), <i>yarin</i> (tomorrow) have no distinctive suffix and appear "
      "frequently as NOUN in the training data (e.g., <i>bugun</i> can also be "
      "a noun meaning 'today/this day'). The model tends to label them as NOUN "
      "when context is insufficient. This accounts for the low ADV recall "
      "(46%) on the custom set.", "body"),
    SP(4),
    P("<b>7.2 ADJ / NOUN boundary</b>", "h2"),
    P("Turkish adjectives and nouns often share identical surface forms. "
      "The word <i>guzel</i> is ADJ in <i>guzel bir gun</i> (a beautiful day) "
      "but NOUN in <i>guzeli sectim</i> (I chose the beautiful one). "
      "Without a following noun or accusative marker, the model frequently "
      "defaults to NOUN, the more common class. This is the largest single "
      "source of errors in both evaluation sets.", "body"),
    SP(4),
    P("<b>7.3 PROPN precision</b>", "h2"),
    P("Proper nouns that appear with suffixes (e.g., <i>Ankara'da</i>, "
      "<i>Turkiye'nin</i>) are identified well due to the apostrophe feature. "
      "However, unseen proper nouns without apostrophes are often misclassified "
      "as NOUN. Conversely, the model sometimes over-predicts PROPN for "
      "capitalised sentence-initial words that are not proper nouns.", "body"),
    SP(12),
    P("8. Conclusion", "h1"), HR(),
    P("This project implements a complete morphological disambiguation system "
      "for Turkish using Conditional Random Fields. The model achieves "
      "<b>90.93% accuracy</b> on the standard UD Turkish-IMST test set and "
      "<b>87.57% accuracy</b> on 25 independently hand-annotated sentences.", "body"),
    SP(6),
    P("Key contributions:", "body"),
    P("• Turkish-specific feature engineering with 40+ morphological features", "bullet"),
    P("• Full CoNLL-U annotation pipeline (training data + manual annotations)", "bullet"),
    P("• Flask web application with live spaCy-style annotation visualisation", "bullet"),
    P("• Per-class evaluation with confusion matrix and F1 charts", "bullet"),
    P("• Error analysis identifying the main sources of misclassification", "bullet"),
    SP(8),
    P("The primary limitation is the ADV/NOUN and ADJ/NOUN confusion for "
      "ambiguous short words. Future work could address this by incorporating "
      "morphological analysis from a dedicated Turkish analyzer (e.g., Zemberek) "
      "as additional input features, or by using a neural sequence model "
      "(BiLSTM-CRF) that captures longer-range context.", "body"),
]

# ─────────────────────────────────────────────────────────
# BUILD PDF
# ─────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUT_PDF,
    pagesize=A4,
    leftMargin=ML, rightMargin=MR,
    topMargin=MT,  bottomMargin=MB + 0.8*cm,
    title=f"{PROJECT_TITLE} — {STUDENT_NAME}",
    author=STUDENT_NAME,
    subject=COURSE,
)
doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
print(f"\nReport generated: {OUT_PDF}\n")
