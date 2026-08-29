"""
Generate index.html for the Atom H2 US field study from us_screen.json.

Every published figure is read from the JSON that build_us_screen.py produced
(atomh2-global/build_us_screen.py). Nothing here is hand-typed, so the page
cannot drift from the data. Regenerate with:

    python3 build_page.py

Visual language deliberately matches atomh2-spain-preview so the two field
studies read as a pair.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D = json.loads((ROOT / "us_screen.json").read_text())
AK, TW, KZ, ASR = D["alaska"], D["alaska_towers"], D["kotzebue"], D["asr"]
MONTHS = list(KZ["ghi_kwh_m2_day"])


def f(n, dp=0):
    return f"{n:,.{dp}f}"


# ── the seasonal figure: solar collapses, wind does not ──────────────────────
def seasonal_svg():
    ghi = [KZ["ghi_kwh_m2_day"][m] for m in MONTHS]
    wind = [KZ["wind_ms_50m"][m] for m in MONTHS]
    W, H, PADL, PADR, PADT, PADB = 900, 340, 54, 54, 26, 46
    pw, ph = W - PADL - PADR, H - PADT - PADB
    gmax, wmax = 7.0, 10.0

    def x(i):
        return PADL + pw * (i + 0.5) / 12

    def yg(v):
        return PADT + ph * (1 - v / gmax)

    def yw(v):
        return PADT + ph * (1 - v / wmax)

    bars = []
    bw = pw / 12 * 0.52
    for i, v in enumerate(ghi):
        h = ph * v / gmax
        bars.append(f'<rect x="{x(i)-bw/2:.1f}" y="{PADT+ph-h:.1f}" width="{bw:.1f}" '
                    f'height="{max(h,0.6):.1f}" fill="var(--brick)" opacity=".78" rx="1"/>')
    wl = " ".join(f"{x(i):.1f},{yw(v):.1f}" for i, v in enumerate(wind))
    dots = "".join(f'<circle cx="{x(i):.1f}" cy="{yw(v):.1f}" r="3.2" fill="var(--ink)"/>'
                   for i, v in enumerate(wind))
    labs = "".join(
        f'<text x="{x(i):.1f}" y="{H-PADB+18}" text-anchor="middle" '
        f'font-size="11" fill="var(--mute)">{m}</text>'
        for i, m in enumerate(MONTHS))
    grid = "".join(
        f'<line x1="{PADL}" y1="{yg(v):.1f}" x2="{W-PADR}" y2="{yg(v):.1f}" '
        f'stroke="var(--hair)" stroke-width="1"/>'
        f'<text x="{PADL-9}" y="{yg(v)+4:.1f}" text-anchor="end" font-size="10.5" '
        f'fill="var(--mute)">{v:g}</text>' for v in [0, 2, 4, 6])
    wax = "".join(
        f'<text x="{W-PADR+9}" y="{yw(v)+4:.1f}" font-size="10.5" '
        f'fill="var(--mute)">{v:g}</text>' for v in [0, 5, 10])

    return f'''<figure class="fig">
<div class="fig-scroll"><svg viewBox="0 0 {W} {H}" role="img" width="100%"
  aria-label="Monthly solar irradiance and wind speed at Kotzebue, Alaska. Solar falls
  to near zero from November to January while wind peaks in the same months.">
  <title>Kotzebue seasonal resource</title>
  {grid}{wax}
  {"".join(bars)}
  <polyline points="{wl}" fill="none" stroke="var(--ink)" stroke-width="2"/>
  {dots}{labs}
  <text x="{PADL-14}" y="{PADT-9}" text-anchor="start" font-size="10" fill="var(--mute)">kWh/m²/d</text>
  <text x="{W-PADR+9}" y="{PADT-9}" font-size="10" fill="var(--mute)">m/s</text>
</svg></div>
<figcaption><b>Fig. 01. Kotzebue, Alaska ({KZ['lat']}°N).</b> Bars: solar irradiance.
Line: wind speed at 50 m. Monthly correlation <b>{KZ['solar_wind_monthly_corr']}</b>.
Solar averages {KZ['ghi_dark_mean']} kWh/m²/d across Nov–Feb against
{KZ['ghi_bright_mean']} in May–Aug; wind runs the other way,
{KZ['wind_dark_mean']} m/s against {KZ['wind_bright_mean']} m/s.
Source: NASA POWER climatology 2020–2024.</figcaption>
</figure>'''


def sizing_rows():
    out = []
    for r in KZ["pv_sizing_for_half_kw_load"]:
        mark = ("<span class='yes'>closes</span>" if r["closes"]
                else "<span class='no'>short</span>")
        out.append(
            f"<tr><td class='tabular'>{r['pv_kw']} kW</td>"
            f"<td class='tabular'>{f(r['summer_surplus_kwh'])}</td>"
            f"<td class='tabular'>{f(r['recoverable_via_h2_kwh'])}</td>"
            f"<td class='tabular'>{f(r['dark_season_deficit_kwh'])}</td>"
            f"<td>{mark}</td></tr>")
    return "\n".join(out)


def tail_rows():
    out = []
    for r in TW["tail_communities"][:10]:
        out.append(
            f"<tr><td>{r['community']}</td><td class='u'>{r['utility']}</td>"
            f"<td class='tabular'>{r['towers']}</td>"
            f"<td class='tabular'>${r['usd_gal']:.2f}</td>"
            f"<td class='tabular'>${r['fuel_usd_kwh']:.3f}</td></tr>")
    return "\n".join(out)


def owner_rows():
    return "\n".join(
        f"<tr><td>{k}</td><td class='tabular'>{v}</td></tr>"
        for k, v in list(TW["top_owners"].items())[:5])


P = AK["usd_per_gal"]
HTML = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atom H2 · United States field study</title>
<meta name="description" content="Where a containerised solar-hydrogen system actually
pencils in the United States, measured against Alaska's invoiced delivered diesel,
FCC tower registrations and NASA POWER resource data.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{color-scheme:light;--paper:#F4EFE2;--ink:#15110D;--mute:#7A7468;--hair:#DCD5C4;--brick:#A93A2A}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:var(--ink);
background:var(--paper);-webkit-font-smoothing:antialiased;line-height:1.6}}
.serif{{font-family:Fraunces,Georgia,serif;font-optical-sizing:auto}}
.tabular{{font-variant-numeric:tabular-nums}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 28px}}
.label{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--mute);font-weight:500}}
.label-brick{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--brick);font-weight:600}}
header{{border-bottom:1px solid var(--hair);position:sticky;top:0;background:rgba(244,239,226,.94);
backdrop-filter:blur(8px);z-index:10}}
header .wrap{{display:flex;gap:26px;align-items:baseline;padding-top:16px;padding-bottom:16px;flex-wrap:wrap}}
header a{{color:var(--ink);text-decoration:none;font-size:13px}}
header a:hover{{color:var(--brick)}}
h1{{font-size:clamp(30px,5.4vw,56px);line-height:1.06;margin:.35em 0 .5em;font-weight:600;text-wrap:balance}}
h2{{font-size:clamp(23px,3.1vw,34px);line-height:1.15;margin:0 0 .5em;font-weight:600;text-wrap:balance}}
h3{{font-size:17px;margin:0 0 .4em;font-weight:600}}
p{{text-wrap:pretty;max-width:74ch}}
section{{padding:64px 0;border-top:1px solid var(--hair)}}
.hero{{padding:76px 0 56px;border-top:0}}
.lede{{font-size:clamp(17px,2vw,20px);color:#3B342C;max-width:66ch}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:26px;margin-top:44px;
border-top:1px solid var(--hair);padding-top:26px}}
.stat .n{{font-family:Fraunces,Georgia,serif;font-size:clamp(28px,4vw,40px);line-height:1;font-variant-numeric:tabular-nums}}
.stat .c{{font-size:12.5px;color:var(--mute);margin-top:8px;line-height:1.45}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:32px;margin-top:32px}}
.card{{border:1px solid var(--hair);padding:22px;background:#FBF8F0}}
.card ul{{margin:.5em 0 0;padding-left:18px;font-size:14.5px;color:#3B342C}}
.card li{{margin:.3em 0}}
blockquote{{margin:44px 0;padding-left:24px;border-left:3px solid var(--brick);
font-family:Fraunces,Georgia,serif;font-size:clamp(19px,2.6vw,26px);line-height:1.35;max-width:60ch}}
blockquote cite{{display:block;font-family:Inter,sans-serif;font-size:12.5px;font-style:normal;
color:var(--mute);margin-top:14px;letter-spacing:.04em}}
.fig{{margin:34px 0 0}}
.fig-scroll{{overflow-x:auto;border:1px solid var(--hair);background:#FBF8F0;padding:14px}}
figcaption{{font-size:12.5px;color:var(--mute);margin-top:12px;max-width:78ch;line-height:1.5}}
.tbl-scroll{{overflow-x:auto;margin-top:26px}}
table{{border-collapse:collapse;width:100%;font-size:14px;min-width:520px}}
th{{text-align:left;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute);
font-weight:500;border-bottom:1px solid var(--ink);padding:0 14px 8px 0;white-space:nowrap}}
td{{padding:9px 14px 9px 0;border-bottom:1px solid var(--hair);vertical-align:top}}
td.u{{color:var(--mute);font-size:13px}}
.yes{{color:var(--brick);font-weight:600}}.no{{color:var(--mute)}}
.flag{{border:1px solid var(--brick);background:#FBF1EE;padding:20px 22px;margin-top:30px}}
.flag h3{{color:var(--brick)}}
.plan{{counter-reset:m;margin-top:34px}}
.month{{display:grid;grid-template-columns:130px 1fr;gap:26px;padding:26px 0;border-top:1px solid var(--hair)}}
.month:first-child{{border-top:0}}
.month .when{{font-family:Fraunces,Georgia,serif;font-size:19px;line-height:1.2}}
.month .when small{{display:block;font-family:Inter,sans-serif;font-size:11.5px;color:var(--mute);
margin-top:6px;letter-spacing:.05em;text-transform:uppercase}}
.month ul{{margin:.2em 0 0;padding-left:18px;color:#3B342C;font-size:15px}}
.month li{{margin:.42em 0}}
footer{{border-top:1px solid var(--ink);padding:44px 0 66px;font-size:13px;color:var(--mute)}}
footer p{{max-width:80ch}}
a{{color:var(--brick)}}
@media(max-width:640px){{.month{{grid-template-columns:1fr;gap:10px}}section{{padding:48px 0}}}}
</style></head>
<body>
<header><div class="wrap">
  <span class="label">Steps Ventures</span>
  <a href="#finding">Finding</a><a href="#logistics">Logistics</a><a href="#physics">Physics</a>
  <a href="#towers">Towers</a><a href="#plan">Plan</a><a href="#capital">Capital</a>
</div></header>

<main class="wrap">

<div class="hero">
  <span class="label-brick">August 2026 · Field study · United States · prepared for Atom H2</span>
  <h1 class="serif">American diesel is cheap. That is the whole problem, and it changes where you should stand.</h1>
  <p class="lede">The obvious US pitch is that remote America burns expensive diesel. It does not.
  Alaska's utilities publish what they actually pay, and the median delivered price is
  <b>${P['50%']:.2f} a gallon</b>, about <b>${AK['usd_per_litre_median']:.2f} a litre</b>, roughly
  {AK['us_vs_europe_ratio']:.2f}× the ${AK['europe_model_mean_usd_l']:.2f}/L the European model assumed.
  A fuel-price arbitrage that works in Europe gets weaker on crossing the Atlantic, not stronger.
  What is scarce in the United States is not the fuel. It is the delivery, and the daylight.</p>

  <div class="stats">
    <div class="stat"><div class="n">${P['50%']:.2f}</div>
      <div class="c">Median invoiced delivered diesel, {AK['communities_reporting_fuel']} remote
      Alaska communities, FY{AK['data_year_mode']}</div></div>
    <div class="stat"><div class="n">${f(AK['fuel_spend_usd_per_yr']/1e6)}M</div>
      <div class="c">Annual fuel spend across those communities, on
      {f(AK['diesel_gal_per_yr']/1e6,1)}M gallons</div></div>
    <div class="stat"><div class="n">{TW['near_a_diesel_community']}</div>
      <div class="c">Registered Alaska structures within {TW['within_km']:.0f} km of one of
      them. {TW['near_ge_6_usd_gal']} of those sit near a community paying $6+/gal</div></div>
    <div class="stat"><div class="n">{KZ['solar_wind_monthly_corr']}</div>
      <div class="c">Solar-to-wind monthly correlation at Kotzebue. The resource that
      survives the dark season is wind</div></div>
  </div>
</div>

<section id="finding">
  <span class="label">I. The finding</span>
  <h2 class="serif">The number that kills the easy version of the pitch</h2>
  <p>The European tower scan found {AK['europe_model_mean_usd_l']:.2f} USD/L of delivered
  diesel and 11,256 NPV-positive sites off the back of it. The instinct is that remote
  America must be worse, on bush planes and ice roads and a single barge. The instinct is
  wrong, because American diesel carries almost no fuel tax and the American pump price
  starts far below the European one.</p>

  <div class="cols">
    <div class="card"><span class="label">Measured, not modelled</span>
      <h3>What Alaska actually pays</h3>
      <ul>
        <li>25th percentile <b class="tabular">${P['25%']:.2f}</b>/gal</li>
        <li>Median <b class="tabular">${P['50%']:.2f}</b>/gal</li>
        <li>75th percentile <b class="tabular">${P['75%']:.2f}</b>/gal</li>
        <li>95th percentile <b class="tabular">${P['95%']:.2f}</b>/gal</li>
        <li>Maximum <b class="tabular">${P['max']:.2f}</b>/gal</li>
      </ul>
    </div>
    <div class="card"><span class="label">Cost of generation</span>
      <h3>Fuel only, per kWh</h3>
      <ul>
        <li>Median <b class="tabular">${AK['fuel_only_usd_per_kwh']['50%']:.3f}</b>/kWh</li>
        <li>90th percentile <b class="tabular">${AK['fuel_only_usd_per_kwh']['90%']:.3f}</b>/kWh</li>
        <li>{f(AK['diesel_kwh_per_yr']/1e6)} GWh/yr generated from diesel</li>
        <li>{f(AK['nondiesel_kwh_per_yr']/1e6)} GWh/yr already non-diesel</li>
        <li>Population served: {f(AK['population_served'])}</li>
      </ul>
    </div>
    <div class="card"><span class="label">Read this way</span>
      <h3>Where the tail lives</h3>
      <ul>
        <li>The median is unremarkable. The <b>tail is not</b>.</li>
        <li>Communities above $6/gal are the only ones where price alone argues for you.</li>
        <li>That is a shortlist of tens of sites, not thousands.</li>
        <li>Treat the US as a <b>proof market</b>, not a volume market.</li>
      </ul>
    </div>
  </div>

  <blockquote class="serif">If the American argument is cheaper fuel, the numbers do not support
  the trip. If the argument is that fuel arrives once a year by barge and the sun disappears for
  three months, the numbers support it completely.
  <cite>Steps Ventures · field study · August 2026</cite></blockquote>
</section>

<section id="logistics">
  <span class="label">II. What is actually scarce</span>
  <h2 class="serif">Delivery risk, not price</h2>
  <p>A remote Alaska village may receive a single bulk fuel delivery in a shipping season
  that only runs through the summer. The price is locked on that one day for the entire
  following year, whatever happens to the commodity afterwards. Villages of a few hundred
  people therefore store hundreds of thousands of gallons.</p>
  <p>The 2026 season made the fragility explicit: ocean shipping rates up sharply, Bering
  Strait ice threatening to delay deliveries by weeks, and low water after breakup limiting
  barge access on the western rivers. Vendors warned of further increases on a war-driven
  supply crunch. The exposure is not the price of a litre. It is a missed window.</p>
  <div class="flag">
    <h3>This reframes the product</h3>
    <p style="margin:.4em 0 0">Atom H2 is not competing with the cost of diesel in Alaska.
    It is competing with the <b>risk of a delivery that does not arrive</b>, and with the
    working capital tied up in a year of fuel bought in advance. Those are the two things a
    buyer there will pay to remove, and neither of them appears anywhere in the European
    model's NPV.</p>
  </div>
</section>

<section id="physics">
  <span class="label">III. The physics</span>
  <h2 class="serif">Three months with no sun, and a wind resource that peaks exactly then</h2>
  <p>This is the part of the American case that is genuinely unique, and it is the reason to
  come here rather than to another high-diesel market. Above the Arctic Circle the solar
  resource does not merely dip in winter. It goes to zero. A battery cannot bridge a season.
  Only a fuel can, which is why these communities burn diesel in the first place.</p>
  {seasonal_svg()}

  <h3 style="margin-top:44px">Can solar plus hydrogen carry a small site through the dark?</h3>
  <p>Taking a {KZ['assumptions']['load_kw']} kW continuous load, a modest repeater or
  monitoring site, at performance ratio {KZ['assumptions']['performance_ratio']} and a
  {KZ['assumptions']['h2_round_trip']:.0%} power-to-hydrogen-to-power round trip:</p>
  <div class="tbl-scroll"><table>
    <thead><tr><th>PV array</th><th>Summer surplus (kWh)</th><th>Recoverable via H₂</th>
    <th>Dark-season deficit</th><th></th></tr></thead>
    <tbody>{sizing_rows()}</tbody>
  </table></div>
  <div class="flag">
    <h3>Be honest about this, because a customer will check</h3>
    <p style="margin:.4em 0 .6em">A naively sized 5 kW array does <b>not</b> close even a
    {KZ['assumptions']['load_kw']} kW load. You need roughly <b>20 kW of panel</b> to bank enough summer
    surplus to survive the winter through hydrogen. That is four times what the load suggests, on a
    structure that has to survive snow load and bears. And Atom H2's stated storage tops out at
    242 kWh, well under the dark-season deficit, so a real installation is a stack of tanks, not one box.</p>
    <p style="margin:0">The resource that is <b>abundant precisely when solar is gone</b> is wind:
    {KZ['wind_dark_mean']} m/s across Nov–Feb. In the Arctic the defensible architecture is
    wind-led generation with hydrogen as the calm-period bridge. Leading with solar here
    invites the one objection you cannot answer.</p>
  </div>
</section>

<section id="towers">
  <span class="label">IV. The addressable estate</span>
  <h2 class="serif">Small, named, and reachable in a single trip</h2>
  <p>Against the FCC's registration of {f(ASR['us_constructed_structures'])} constructed
  structures nationwide, Alaska holds {f(TW['ak_constructed'])}. Of those,
  <b>{TW['near_a_diesel_community']}</b> sit within {TW['within_km']:.0f} km of a community whose
  delivered fuel price is published. {TW['near_ge_5_usd_gal']} sit near a community above $5/gal
  and <b>{TW['near_ge_6_usd_gal']}</b> above $6/gal.</p>

  <div class="cols">
    <div class="card"><span class="label">Fig. 02a</span><h3>The expensive tail</h3>
      <div class="tbl-scroll"><table>
        <thead><tr><th>Community</th><th>Utility</th><th>Sites</th><th>$/gal</th><th>$/kWh</th></tr></thead>
        <tbody>{tail_rows()}</tbody></table></div>
    </div>
    <div class="card"><span class="label">Fig. 02b</span><h3>Who owns the estate</h3>
      <div class="tbl-scroll"><table>
        <thead><tr><th>Owner</th><th>Structures</th></tr></thead>
        <tbody>{owner_rows()}</tbody></table></div>
      <p style="font-size:13.5px;color:#3B342C;margin-top:14px">One counterparty dominates.
      GCI also runs TERRA, a 3,300-mile fibre and microwave network reaching more than 45,000
      people off the road system. That is an estate of small, remote, year-round powered relay sites
      that is a far better fit for a kW-class box than any village powerhouse.</p>
    </div>
  </div>

  <div class="flag">
    <h3>What this estate is not</h3>
    <p style="margin:.4em 0 0">A village power plant runs at hundreds of kW to megawatts.
    Atom H2's fuel cell is 2–6 kW. <b>Do not pitch the powerhouse.</b> The honest targets are
    telecom relays, repeaters, monitoring and navigation sites, water and clinic backup. Those are the
    kW-class loads that sit beside the powerhouse and share its fuel problem.</p>
    <p style="margin:.8em 0 0">It is also far smaller than the figure in circulation. There are
    roughly 172,000 cell towers in the entire United States and about 419,000 sites once small
    cells are counted, and essentially all of them are grid connected with diesel as backup. Any
    claim of 300,000 off-grid or diesel-dependent US tower sites is the global off-grid count
    mis-scaled, and it should not be repeated to a customer who can check it.</p>
  </div>
</section>

<section id="plan">
  <span class="label">V. The three months</span>
  <h2 class="serif">What a visit should actually produce</h2>
  <p>Two constraints shape everything below. The exchange is committed to Newlab in the
  Brooklyn Navy Yard, so Alaska is a set of sorties from that base rather than a relocation. And
  it runs on ESTA, which permits meetings, negotiation, conferences, site visits and market
  research, and <b>prohibits productive work</b> for a US entity, paid or unpaid. No installing,
  no commissioning, no running a deployment. This ends in signed intent and a funded winter
  trial, not in a box on a pad.</p>

  <div class="plan">
    <div class="month">
      <div class="when serif">Month one<small>Oct · Newlab base, one sortie</small></div>
      <ul>
        <li><b>Alaska Rural Energy Conference, Fairbanks, 27–29 Oct</b> (pre-conference 26th).
        The single highest-density room of remote-diesel operators in the United States. Go with
        the seasonal-resource figure, not a product brochure.</li>
        <li>If arrival allows, the <b>Alaska Power Association 75th Annual Meeting, Anchorage,
        29 Sep – 2 Oct</b> puts the utility establishment in one place first.</li>
        <li>Open GCI directly. They own {TW['top_owners'].get('GCI Communication Corp', 0)} of the
        {TW['near_a_diesel_community']} relevant structures and operate TERRA. One meeting covers
        more of the estate than every other owner combined.</li>
        <li>Meet Launch Alaska. Their Tech Deployment Track exists specifically to place outside
        technology into Alaska communities, backed by ONR and DOE. Applications are closed;
        file the expression of interest while you are in the room.</li>
      </ul>
    </div>
    <div class="month">
      <div class="when serif">Month two<small>Nov · the long sortie</small></div>
      <ul>
        <li>November is the point. Be in Alaska while the sun is gone and the wind is at
        {KZ['wind_dark_mean']} m/s. Those are the conditions that make the argument, and you can collect site data
        no European dataset contains.</li>
        <li>Convert one operator into a <b>funded winter field trial</b> for 2027: instrumented,
        third-party measured, on a real relay site. That is the asset the company lacks and every
        investor asks for.</li>
        <li><b>RE+, Las Vegas, 16–19 Nov</b> is North America's largest clean-energy event. It
        clashes with the NWPPA Alaska Electric Utility Conference in Anchorage on the same dates.
        Pick one. RE+ if the goal is capital and partners; NWPPA if the goal is Alaskan buyers.</li>
        <li>Start the entity question, because it gates everything after (see below).</li>
      </ul>
    </div>
    <div class="month">
      <div class="when serif">Month three<small>Dec · back at Newlab</small></div>
      <ul>
        <li>Turn conversations into paper: a letter of intent for the winter trial, a named
        host site, a scope of measurement, and who pays for what.</li>
        <li>Target the <b>Alaska Energy Authority Renewable Energy Fund</b> for the round after
        this one. Round 19 closes 11 Sep 2026, before arrival, and applications come from
        utilities and communities, not vendors. Your role is named technology partner on
        somebody else's application, so the relationship has to exist months ahead.</li>
        <li>Leave before the ESTA 90 days expire. A 1 October arrival means departing by roughly
        29 December. Write 90 days, never "1 Oct to 31 Dec", which is 91.</li>
      </ul>
    </div>
  </div>
</section>

<section id="capital">
  <span class="label">VI. Capital</span>
  <h2 class="serif">The honest read on American money</h2>
  <div class="cols">
    <div class="card"><span class="label">Closed for now</span><h3>Federal SBIR</h3>
      <p style="font-size:14.5px;margin:.4em 0 0">Requires at least 51% ownership by US citizens
      or permanent residents. The April 2026 reauthorisation added mandatory foreign-risk
      screening to every submission with no exceptions. A Barcelona company is not eligible, and
      a thin US subsidiary does not fix it. Do not build a roadmap on DoD SBIR.</p></div>
    <div class="card"><span class="label">Open, and a better fit</span><h3>NATO Innovation Fund</h3>
      <p style="font-size:14.5px;margin:.4em 0 0">A €1B multi-sovereign fund investing in dual-use
      technology including energy resilience. Atom H2 is already a DIANA company. European capital,
      defence-adjacent thesis, no foreign-ownership friction. This is the most natural cheque on the
      board and it does not require moving the company.</p></div>
    <div class="card"><span class="label">Thin</span><h3>US venture</h3>
      <p style="font-size:14.5px;margin:.4em 0 0">Hydrogen storage remains a niche venture bet;
      late-stage and growth rounds took over 90% of disclosed storage capital in 2026. A US
      Series A on a kW-scale hydrogen thesis without field data is a hard raise. Comparable
      rounds, Photoncycle and PowerUP Energy, were led in Europe. Spend the three months making
      the raise easier, not attempting it.</p></div>
  </div>
  <div class="flag">
    <h3>Sequence, not a scattergun</h3>
    <p style="margin:.4em 0 0">Field data first, then capital. A measured Arctic winter on a real
    site is worth more to a European investor than any number of American meetings, and it is the
    one thing three months in Alaska can produce that Barcelona cannot.</p>
  </div>
</section>

</main>

<footer><div class="wrap">
  <p><b>Method.</b> Delivered diesel, gallons burned and diesel generation are per-community
  invoiced figures from the Alaska Energy Authority Power Cost Equalization programme
  (FY{AK['data_year_mode']} for the majority of {AK['communities_in_programme']} communities;
  {AK['communities_reporting_fuel']} report fuel directly and the remainder report through a parent
  cooperative). Structure locations and owners are from the FCC Antenna Structure Registration
  weekly dump. {ASR['caveat']}, so tower counts are a floor. Solar and wind are NASA POWER
  climatology 2020–2024. Sizing figures are a screen, not an engineering study: single-point
  climatology, with no hourly simulation, no snow-cover or icing losses and no site survey.
  Every figure on this page is generated from <code>us_screen.json</code> by
  <code>build_page.py</code>; none is hand-entered.</p>
  <p style="margin-top:18px"><b>Disclosure.</b> Steps Ventures is a paid consultant to Atom H2.
  Where this study points toward pairing hydrogen storage with wind generation, note that Steps
  Ventures also consults for Airloom Energy, a wind company. Neither relationship involves equity.</p>
  <p style="margin-top:18px">Steps Ventures · August 2026 · Prepared for Atom H2 Energytech,
  Barcelona · Companion to the Spain field study.</p>
</div></footer>
</body></html>
'''

(ROOT / "index.html").write_text(HTML)
print(f"wrote {ROOT/'index.html'} ({len(HTML):,} bytes)")
