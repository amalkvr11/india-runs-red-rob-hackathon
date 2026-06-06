import{B as A,C as W,D as O,o as c,c as m,E as G,G as z,t as d,b as P,d as L,H,f as R,u as T,l as q,h as s,g as i,x as $,w as u,a as t,e as g,y as J,I as K,F as x,r as M,z as U,i as y,k as Y,j as Q,J as X}from"./index-DD9HJRoY.js";import{s as _}from"./index-DtWtQ5bU.js";import{a as Z,s as b}from"./index-CarGWZZp.js";import{_ as ee}from"./_plugin-vue_export-helper-DlAUqK2U.js";var ae=`
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
`,te={root:function(r){var p=r.props;return["p-avatar p-component",{"p-avatar-image":p.image!=null,"p-avatar-circle":p.shape==="circle","p-avatar-lg":p.size==="large","p-avatar-xl":p.size==="xlarge"}]},label:"p-avatar-label",icon:"p-avatar-icon"},re=A.extend({name:"avatar",style:ae,classes:te}),ne={name:"BaseAvatar",extends:W,props:{label:{type:String,default:null},icon:{type:String,default:null},image:{type:String,default:null},size:{type:String,default:"normal"},shape:{type:String,default:"square"},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null}},style:re,provide:function(){return{$pcAvatar:this,$parentInstance:this}}};function h(a){"@babel/helpers - typeof";return h=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(r){return typeof r}:function(r){return r&&typeof Symbol=="function"&&r.constructor===Symbol&&r!==Symbol.prototype?"symbol":typeof r},h(a)}function C(a,r,p){return(r=ie(r))in a?Object.defineProperty(a,r,{value:p,enumerable:!0,configurable:!0,writable:!0}):a[r]=p,a}function ie(a){var r=le(a,"string");return h(r)=="symbol"?r:r+""}function le(a,r){if(h(a)!="object"||!a)return a;var p=a[Symbol.toPrimitive];if(p!==void 0){var v=p.call(a,r);if(h(v)!="object")return v;throw new TypeError("@@toPrimitive must return a primitive value.")}return(r==="string"?String:Number)(a)}var B={name:"Avatar",extends:ne,inheritAttrs:!1,emits:["error"],methods:{onError:function(r){this.$emit("error",r)}},computed:{dataP:function(){return O(C(C({},this.shape,this.shape),this.size,this.size))}}},se=["aria-labelledby","aria-label","data-p"],oe=["data-p"],de=["data-p"],pe=["src","alt","data-p"];function ue(a,r,p,v,o,f){return c(),m("div",z({class:a.cx("root"),"aria-labelledby":a.ariaLabelledby,"aria-label":a.ariaLabel},a.ptmi("root"),{"data-p":f.dataP}),[G(a.$slots,"default",{},function(){return[a.label?(c(),m("span",z({key:0,class:a.cx("label")},a.ptm("label"),{"data-p":f.dataP}),d(a.label),17,oe)):a.$slots.icon?(c(),P(H(a.$slots.icon),{key:1,class:L(a.cx("icon"))},null,8,["class"])):a.icon?(c(),m("span",z({key:2,class:[a.cx("icon"),a.icon]},a.ptm("icon"),{"data-p":f.dataP}),null,16,de)):a.image?(c(),m("img",z({key:3,src:a.image,alt:a.ariaLabel,onError:r[0]||(r[0]=function(){return f.onError&&f.onError.apply(f,arguments)})},a.ptm("image"),{"data-p":f.dataP}),null,16,pe)):R("",!0)]})],16,se)}B.render=ue;const ce={key:0,class:"detail-view"},ve={class:"detail-header"},me={class:"header-left"},fe={class:"detail-title"},ge={class:"detail-loc"},ye={class:"header-right"},be={class:"big-score"},he={class:"detail-grid"},we={class:"field-label"},ke={class:"field-value"},ze={class:"dim-name-cell"},xe={class:"dim-score-bar"},_e={class:"dim-score-val"},Se={class:"reasoning-text"},$e={key:1,class:"empty-detail"},Ce={__name:"CandidateDetailView",setup(a){const r=X(),p=Y(),v=T();q(()=>{v.ensureLoaded()});const o=y(()=>v.getCandidate(r.params.id)),f=y(()=>{var e;const l=((e=o.value)==null?void 0:e.rank)||0;return l<=10?"danger":l<=30?"warn":l<=60?"info":"contrast"}),E=y(()=>{const l=o.value;if(!l)return[];const e=l.profile||{};return[{label:"Name",value:e.anonymized_name||"-"},{label:"Current Title",value:l.current_title||"-"},{label:"Company",value:l.current_company||"-"},{label:"Location",value:[e.location,e.country].filter(Boolean).join(", ")||"-"},{label:"Years of Exp",value:e.years_of_experience??"-"},{label:"Industry",value:e.current_industry||"-"},{label:"Company Size",value:e.current_company_size||"-"},{label:"Headline",value:(e.headline||"").slice(0,80)||"-"}]}),F={title_role:"pi pi-id-card",skills:"pi pi-cog",career_quality:"pi pi-building",experience:"pi pi-clock",statement:"pi pi-pen",behavioral:"pi pi-heart",location:"pi pi-map-marker",education:"pi pi-book"},w=y(()=>{const l=o.value;return!l||!v.weights?[]:Object.entries(v.weights).map(([e,S])=>{var n;return{key:e,label:e.replace(/_/g," ").replace(/\b\w/g,k=>k.toUpperCase()),icon:F[e]||"pi pi-circle",score:l.sub_scores[e]||0,weight:S,reasoning:((n=l.reasonings)==null?void 0:n[e])||""}})}),j=y(()=>w.value.map(l=>l.label)),D=y(()=>w.value.map(l=>l.score)),N=y(()=>w.value.map(l=>l.weight)),V=y(()=>[{name:"Score",data:D.value},{name:"Weight",data:N.value}]),I={chart:{type:"radar",toolbar:{show:!1},fontFamily:"Inter"},colors:["#00bcd4","#ff9800"],xaxis:{categories:j.value,labels:{style:{colors:"#e4e6f0"}}},yaxis:{show:!1,min:0,max:1},markers:{size:5},stroke:{width:2},fill:{opacity:.1},tooltip:{theme:"dark"},legend:{labels:{colors:"#e4e6f0"}}};return(l,e)=>{const S=Q("apexchart");return o.value?(c(),m("div",ce,[s(i($),{icon:"pi pi-arrow-left",text:"",onClick:e[0]||(e[0]=n=>i(p).push("/results")),label:"Back to Results",class:"back-btn"}),s(i(_),{class:"detail-header-card"},{content:u(()=>{var n,k;return[t("div",ve,[t("div",me,[s(i(B),{label:((n=o.value.name)==null?void 0:n[0])||"?",shape:"circle",size:"xlarge",style:{background:"var(--p-primary-500)",color:"#fff"}},null,8,["label"]),t("div",null,[t("h2",null,d(o.value.candidate_id),1),t("p",fe,[g(d(o.value.current_title)+" ",1),e[3]||(e[3]=t("span",{class:"at-text"},"at",-1)),g(" "+d(o.value.current_company),1)]),t("p",ge,[e[4]||(e[4]=t("i",{class:"pi pi-map-marker"},null,-1)),g(" "+d(o.value.location),1)])])]),t("div",ye,[s(i(J),{value:`Rank #${o.value.rank}`,severity:f.value,size:"large"},null,8,["value","severity"]),t("div",be,d(o.value.score.toFixed(4)),1),e[5]||(e[5]=t("span",{class:"score-label"},"Overall Score",-1))])]),(k=o.value.honeypot)!=null&&k.is_honeypot?(c(),P(i(K),{key:0,severity:"warn",closable:!1,class:"honey-msg"},{default:u(()=>[e[6]||(e[6]=t("i",{class:"pi pi-exclamation-triangle"},null,-1)),g(" Honeypot detected: "+d(o.value.honeypot.flags.join(", "))+" — Penalty: "+d((o.value.honeypot.penalty*100).toFixed(0))+"% ",1)]),_:1})):R("",!0)]}),_:1}),t("div",he,[s(i(_),null,{title:u(()=>[...e[7]||(e[7]=[t("i",{class:"pi pi-user"},null,-1),g(" Profile Summary",-1)])]),content:u(()=>[(c(!0),m(x,null,M(E.value,n=>(c(),m("div",{class:"profile-field",key:n.label},[t("span",we,d(n.label),1),t("span",ke,d(n.value),1)]))),128))]),_:1}),s(i(_),null,{title:u(()=>[...e[8]||(e[8]=[t("i",{class:"pi pi-chart-pie"},null,-1),g(" Scores vs Weights",-1)])]),content:u(()=>[s(S,{type:"radar",height:"340",options:I,series:V.value},null,8,["series"])]),_:1})]),s(i(_),null,{title:u(()=>[...e[9]||(e[9]=[t("i",{class:"pi pi-table"},null,-1),g(" Dimension Breakdown",-1)])]),content:u(()=>[s(i(Z),{value:w.value,stripedRows:"",showGridlines:"",class:"dims-table"},{default:u(()=>[s(i(b),{field:"label",header:"Dimension"},{body:u(({data:n})=>[t("div",ze,[t("i",{class:L(n.icon)},null,2),g(" "+d(n.label),1)])]),_:1}),s(i(b),{field:"score",header:"Score",style:{width:"160px"}},{body:u(({data:n})=>[t("div",xe,[s(i(U),{value:n.score*100,showValue:!1},null,8,["value"]),t("span",_e,d(n.score.toFixed(3)),1)])]),_:1}),s(i(b),{field:"weight",header:"Weight",style:{width:"70px"}},{body:u(({data:n})=>[g(d(n.weight.toFixed(2)),1)]),_:1}),s(i(b),{field:"weighted",header:"Weighted",style:{width:"90px"}},{body:u(({data:n})=>[t("strong",null,d((n.score*n.weight).toFixed(4)),1)]),_:1}),s(i(b),{field:"reasoning",header:"Reasoning"},{body:u(({data:n})=>[t("span",Se,d(n.reasoning),1)]),_:1})]),_:1},8,["value"])]),_:1})])):(c(),m("div",$e,[i(v).loading?(c(),m(x,{key:0},[e[10]||(e[10]=t("i",{class:"pi pi-spin pi-spinner",style:{"font-size":"2rem"}},null,-1)),e[11]||(e[11]=t("p",null,"Loading candidates...",-1))],64)):i(v).results?(c(),m(x,{key:2},[e[14]||(e[14]=t("i",{class:"pi pi-exclamation-circle",style:{"font-size":"2rem"}},null,-1)),e[15]||(e[15]=t("p",null,"Candidate not found in results",-1)),s(i($),{label:"Go to Results",icon:"pi pi-arrow-left",onClick:e[2]||(e[2]=n=>i(p).push("/results")),severity:"info"})],64)):(c(),m(x,{key:1},[e[12]||(e[12]=t("i",{class:"pi pi-database",style:{"font-size":"2rem"}},null,-1)),e[13]||(e[13]=t("p",null,"No candidate data loaded",-1)),s(i($),{label:"Load Results",icon:"pi pi-refresh",onClick:e[1]||(e[1]=n=>i(v).ensureLoaded()),severity:"info"})],64))]))}}},Ee=ee(Ce,[["__scopeId","data-v-079565cd"]]);export{Ee as default};
