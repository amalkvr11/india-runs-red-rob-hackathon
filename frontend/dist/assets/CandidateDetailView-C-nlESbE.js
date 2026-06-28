import{D as I,E as W,G as O,o as c,c as m,H as G,I as z,t as d,b as P,d as L,J as H,f as R,u as T,l as q,h as s,g as i,y as $,w as u,a as t,e as g,z as K,K as J,F as x,r as M,A as U,i as y,k as Y,j as Q,L as X}from"./index-B5ctDXGs.js";import{s as _}from"./index-BB558xRc.js";import{a as Z,s as b}from"./index-CHpbxcdV.js";import{_ as aa}from"./_plugin-vue_export-helper-DlAUqK2U.js";var ea=`
    .p-avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: dt('avatar.width');
        height: dt('avatar.height');
        font-size: dt('avatar.font.size');
        background: dt('avatar.background');
        color: dt('avatar.color');
        border-radius: dt('avatar.border.radius');
    }

    .p-avatar-image {
        background: transparent;
    }

    .p-avatar-circle {
        border-radius: 50%;
    }

    .p-avatar-circle img {
        border-radius: 50%;
    }

    .p-avatar-icon {
        font-size: dt('avatar.icon.size');
        width: dt('avatar.icon.size');
        height: dt('avatar.icon.size');
    }

    .p-avatar img {
        width: 100%;
        height: 100%;
    }

    .p-avatar-lg {
        width: dt('avatar.lg.width');
        height: dt('avatar.lg.width');
        font-size: dt('avatar.lg.font.size');
    }

    .p-avatar-lg .p-avatar-icon {
        font-size: dt('avatar.lg.icon.size');
        width: dt('avatar.lg.icon.size');
        height: dt('avatar.lg.icon.size');
    }

    .p-avatar-xl {
        width: dt('avatar.xl.width');
        height: dt('avatar.xl.width');
        font-size: dt('avatar.xl.font.size');
    }

    .p-avatar-xl .p-avatar-icon {
        font-size: dt('avatar.xl.icon.size');
        width: dt('avatar.xl.icon.size');
        height: dt('avatar.xl.icon.size');
    }

    .p-avatar-group {
        display: flex;
        align-items: center;
    }

    .p-avatar-group .p-avatar + .p-avatar {
        margin-inline-start: dt('avatar.group.offset');
    }

    .p-avatar-group .p-avatar {
        border: 2px solid dt('avatar.group.border.color');
    }

    .p-avatar-group .p-avatar-lg + .p-avatar-lg {
        margin-inline-start: dt('avatar.lg.group.offset');
    }

    .p-avatar-group .p-avatar-xl + .p-avatar-xl {
        margin-inline-start: dt('avatar.xl.group.offset');
    }
`,ta={root:function(r){var p=r.props;return["p-avatar p-component",{"p-avatar-image":p.image!=null,"p-avatar-circle":p.shape==="circle","p-avatar-lg":p.size==="large","p-avatar-xl":p.size==="xlarge"}]},label:"p-avatar-label",icon:"p-avatar-icon"},ra=I.extend({name:"avatar",style:ea,classes:ta}),na={name:"BaseAvatar",extends:W,props:{label:{type:String,default:null},icon:{type:String,default:null},image:{type:String,default:null},size:{type:String,default:"normal"},shape:{type:String,default:"square"},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null}},style:ra,provide:function(){return{$pcAvatar:this,$parentInstance:this}}};function h(e){"@babel/helpers - typeof";return h=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(r){return typeof r}:function(r){return r&&typeof Symbol=="function"&&r.constructor===Symbol&&r!==Symbol.prototype?"symbol":typeof r},h(e)}function C(e,r,p){return(r=ia(r))in e?Object.defineProperty(e,r,{value:p,enumerable:!0,configurable:!0,writable:!0}):e[r]=p,e}function ia(e){var r=la(e,"string");return h(r)=="symbol"?r:r+""}function la(e,r){if(h(e)!="object"||!e)return e;var p=e[Symbol.toPrimitive];if(p!==void 0){var v=p.call(e,r);if(h(v)!="object")return v;throw new TypeError("@@toPrimitive must return a primitive value.")}return(r==="string"?String:Number)(e)}var B={name:"Avatar",extends:na,inheritAttrs:!1,emits:["error"],methods:{onError:function(r){this.$emit("error",r)}},computed:{dataP:function(){return O(C(C({},this.shape,this.shape),this.size,this.size))}}},sa=["aria-labelledby","aria-label","data-p"],oa=["data-p"],da=["data-p"],pa=["src","alt","data-p"];function ua(e,r,p,v,o,f){return c(),m("div",z({class:e.cx("root"),"aria-labelledby":e.ariaLabelledby,"aria-label":e.ariaLabel},e.ptmi("root"),{"data-p":f.dataP}),[G(e.$slots,"default",{},function(){return[e.label?(c(),m("span",z({key:0,class:e.cx("label")},e.ptm("label"),{"data-p":f.dataP}),d(e.label),17,oa)):e.$slots.icon?(c(),P(H(e.$slots.icon),{key:1,class:L(e.cx("icon"))},null,8,["class"])):e.icon?(c(),m("span",z({key:2,class:[e.cx("icon"),e.icon]},e.ptm("icon"),{"data-p":f.dataP}),null,16,da)):e.image?(c(),m("img",z({key:3,src:e.image,alt:e.ariaLabel,onError:r[0]||(r[0]=function(){return f.onError&&f.onError.apply(f,arguments)})},e.ptm("image"),{"data-p":f.dataP}),null,16,pa)):R("",!0)]})],16,sa)}B.render=ua;const ca={key:0,class:"detail-view"},va={class:"detail-header"},ma={class:"header-left"},fa={class:"detail-title"},ga={class:"detail-loc"},ya={class:"header-right"},ba={class:"big-score"},ha={class:"detail-grid"},wa={class:"field-label"},ka={class:"field-value"},za={class:"dim-name-cell"},xa={class:"dim-score-bar"},_a={class:"dim-score-val"},Sa={class:"reasoning-text"},$a={key:1,class:"empty-detail"},Ca={__name:"CandidateDetailView",setup(e){const r=X(),p=Y(),v=T();q(()=>{v.ensureLoaded()});const o=y(()=>v.getCandidate(r.params.id)),f=y(()=>{var a;const l=((a=o.value)==null?void 0:a.rank)||0;return l<=10?"danger":l<=30?"warn":l<=60?"info":"contrast"}),E=y(()=>{const l=o.value;if(!l)return[];const a=l.profile||{};return[{label:"Name",value:a.anonymized_name||"-"},{label:"Current Title",value:l.current_title||"-"},{label:"Company",value:l.current_company||"-"},{label:"Location",value:[a.location,a.country].filter(Boolean).join(", ")||"-"},{label:"Years of Exp",value:a.years_of_experience??"-"},{label:"Industry",value:a.current_industry||"-"},{label:"Company Size",value:a.current_company_size||"-"},{label:"Headline",value:(a.headline||"").slice(0,80)||"-"}]}),F={title_role:"pi pi-id-card",skills:"pi pi-cog",career_quality:"pi pi-building",experience:"pi pi-clock",statement:"pi pi-pen",behavioral:"pi pi-heart",location:"pi pi-map-marker",education:"pi pi-book"},w=y(()=>{const l=o.value;return!l||!v.weights?[]:Object.entries(v.weights).map(([a,S])=>{var n;return{key:a,label:a.replace(/_/g," ").replace(/\b\w/g,k=>k.toUpperCase()),icon:F[a]||"pi pi-circle",score:l.sub_scores[a]||0,weight:S,reasoning:((n=l.reasonings)==null?void 0:n[a])||""}})}),j=y(()=>w.value.map(l=>l.label)),D=y(()=>w.value.map(l=>l.score)),N=y(()=>w.value.map(l=>l.weight)),V=y(()=>[{name:"Score",data:D.value},{name:"Weight",data:N.value}]),A={chart:{type:"radar",toolbar:{show:!1},fontFamily:"Inter"},colors:["#00bcd4","#ff9800"],xaxis:{categories:j.value,labels:{style:{colors:"#e4e6f0"}}},yaxis:{show:!1,min:0,max:1},markers:{size:5},stroke:{width:2},fill:{opacity:.1},tooltip:{theme:"dark"},legend:{labels:{colors:"#e4e6f0"}}};return(l,a)=>{const S=Q("apexchart");return o.value?(c(),m("div",ca,[s(i($),{icon:"pi pi-arrow-left",text:"",onClick:a[0]||(a[0]=n=>i(p).push("/results")),label:"Back to Results",class:"back-btn"}),s(i(_),{class:"detail-header-card"},{content:u(()=>{var n,k;return[t("div",va,[t("div",ma,[s(i(B),{label:((n=o.value.name)==null?void 0:n[0])||"?",shape:"circle",size:"xlarge",style:{background:"var(--p-primary-500)",color:"#fff"}},null,8,["label"]),t("div",null,[t("h2",null,d(o.value.candidate_id),1),t("p",fa,[g(d(o.value.current_title)+" ",1),a[3]||(a[3]=t("span",{class:"at-text"},"at",-1)),g(" "+d(o.value.current_company),1)]),t("p",ga,[a[4]||(a[4]=t("i",{class:"pi pi-map-marker"},null,-1)),g(" "+d(o.value.location),1)])])]),t("div",ya,[s(i(K),{value:`Rank #${o.value.rank}`,severity:f.value,size:"large"},null,8,["value","severity"]),t("div",ba,d(o.value.score.toFixed(4)),1),a[5]||(a[5]=t("span",{class:"score-label"},"Overall Score",-1))])]),(k=o.value.honeypot)!=null&&k.is_honeypot?(c(),P(i(J),{key:0,severity:"warn",closable:!1,class:"honey-msg"},{default:u(()=>[a[6]||(a[6]=t("i",{class:"pi pi-exclamation-triangle"},null,-1)),g(" Honeypot detected: "+d(o.value.honeypot.flags.join(", "))+" — Penalty: "+d((o.value.honeypot.penalty*100).toFixed(0))+"% ",1)]),_:1})):R("",!0)]}),_:1}),t("div",ha,[s(i(_),null,{title:u(()=>[...a[7]||(a[7]=[t("i",{class:"pi pi-user"},null,-1),g(" Profile Summary",-1)])]),content:u(()=>[(c(!0),m(x,null,M(E.value,n=>(c(),m("div",{class:"profile-field",key:n.label},[t("span",wa,d(n.label),1),t("span",ka,d(n.value),1)]))),128))]),_:1}),s(i(_),null,{title:u(()=>[...a[8]||(a[8]=[t("i",{class:"pi pi-chart-pie"},null,-1),g(" Scores vs Weights",-1)])]),content:u(()=>[s(S,{type:"radar",height:"340",options:A,series:V.value},null,8,["series"])]),_:1})]),s(i(_),null,{title:u(()=>[...a[9]||(a[9]=[t("i",{class:"pi pi-table"},null,-1),g(" Dimension Breakdown",-1)])]),content:u(()=>[s(i(Z),{value:w.value,stripedRows:"",showGridlines:"",class:"dims-table"},{default:u(()=>[s(i(b),{field:"label",header:"Dimension"},{body:u(({data:n})=>[t("div",za,[t("i",{class:L(n.icon)},null,2),g(" "+d(n.label),1)])]),_:1}),s(i(b),{field:"score",header:"Score",style:{width:"160px"}},{body:u(({data:n})=>[t("div",xa,[s(i(U),{value:n.score*100,showValue:!1},null,8,["value"]),t("span",_a,d(n.score.toFixed(3)),1)])]),_:1}),s(i(b),{field:"weight",header:"Weight",style:{width:"70px"}},{body:u(({data:n})=>[g(d(n.weight.toFixed(2)),1)]),_:1}),s(i(b),{field:"weighted",header:"Weighted",style:{width:"90px"}},{body:u(({data:n})=>[t("strong",null,d((n.score*n.weight).toFixed(4)),1)]),_:1}),s(i(b),{field:"reasoning",header:"Reasoning"},{body:u(({data:n})=>[t("span",Sa,d(n.reasoning),1)]),_:1})]),_:1},8,["value"])]),_:1})])):(c(),m("div",$a,[i(v).loading?(c(),m(x,{key:0},[a[10]||(a[10]=t("i",{class:"pi pi-spin pi-spinner",style:{"font-size":"2rem"}},null,-1)),a[11]||(a[11]=t("p",null,"Loading candidates...",-1))],64)):i(v).results?(c(),m(x,{key:2},[a[14]||(a[14]=t("i",{class:"pi pi-exclamation-circle",style:{"font-size":"2rem"}},null,-1)),a[15]||(a[15]=t("p",null,"Candidate not found in results",-1)),s(i($),{label:"Go to Results",icon:"pi pi-arrow-left",onClick:a[2]||(a[2]=n=>i(p).push("/results")),severity:"info"})],64)):(c(),m(x,{key:1},[a[12]||(a[12]=t("i",{class:"pi pi-database",style:{"font-size":"2rem"}},null,-1)),a[13]||(a[13]=t("p",null,"No candidate data loaded",-1)),s(i($),{label:"Load Results",icon:"pi pi-refresh",onClick:a[1]||(a[1]=n=>i(v).ensureLoaded()),severity:"info"})],64))]))}}},Ea=aa(Ca,[["__scopeId","data-v-bfa9d264"]]);export{Ea as default};
