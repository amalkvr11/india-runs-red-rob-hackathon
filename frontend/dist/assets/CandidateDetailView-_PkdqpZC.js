import{B as A,A as I,C as N,o as u,c as g,D as W,E as x,t as d,b as $,d as C,G as O,f as P,u as H,h as o,g as l,y as T,w as p,a as r,e as m,v as q,H as G,F as K,r as U,x as Y,i as f,k as J,j as M,I as Q}from"./index-o0pIy1jI.js";import{s as z}from"./index-CStQab54.js";import{a as X,s as b}from"./index-UbB4_OTC.js";import{_ as Z}from"./_plugin-vue_export-helper-DlAUqK2U.js";var aa=`
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
`,ea={root:function(t){var c=t.props;return["p-avatar p-component",{"p-avatar-image":c.image!=null,"p-avatar-circle":c.shape==="circle","p-avatar-lg":c.size==="large","p-avatar-xl":c.size==="xlarge"}]},label:"p-avatar-label",icon:"p-avatar-icon"},ta=A.extend({name:"avatar",style:aa,classes:ea}),ra={name:"BaseAvatar",extends:I,props:{label:{type:String,default:null},icon:{type:String,default:null},image:{type:String,default:null},size:{type:String,default:"normal"},shape:{type:String,default:"square"},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null}},style:ta,provide:function(){return{$pcAvatar:this,$parentInstance:this}}};function y(a){"@babel/helpers - typeof";return y=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(t){return typeof t}:function(t){return t&&typeof Symbol=="function"&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},y(a)}function S(a,t,c){return(t=na(t))in a?Object.defineProperty(a,t,{value:c,enumerable:!0,configurable:!0,writable:!0}):a[t]=c,a}function na(a){var t=ia(a,"string");return y(t)=="symbol"?t:t+""}function ia(a,t){if(y(a)!="object"||!a)return a;var c=a[Symbol.toPrimitive];if(c!==void 0){var h=c.call(a,t);if(y(h)!="object")return h;throw new TypeError("@@toPrimitive must return a primitive value.")}return(t==="string"?String:Number)(a)}var B={name:"Avatar",extends:ra,inheritAttrs:!1,emits:["error"],methods:{onError:function(t){this.$emit("error",t)}},computed:{dataP:function(){return N(S(S({},this.shape,this.shape),this.size,this.size))}}},la=["aria-labelledby","aria-label","data-p"],sa=["data-p"],oa=["data-p"],da=["src","alt","data-p"];function pa(a,t,c,h,s,v){return u(),g("div",x({class:a.cx("root"),"aria-labelledby":a.ariaLabelledby,"aria-label":a.ariaLabel},a.ptmi("root"),{"data-p":v.dataP}),[W(a.$slots,"default",{},function(){return[a.label?(u(),g("span",x({key:0,class:a.cx("label")},a.ptm("label"),{"data-p":v.dataP}),d(a.label),17,sa)):a.$slots.icon?(u(),$(O(a.$slots.icon),{key:1,class:C(a.cx("icon"))},null,8,["class"])):a.icon?(u(),g("span",x({key:2,class:[a.cx("icon"),a.icon]},a.ptm("icon"),{"data-p":v.dataP}),null,16,oa)):a.image?(u(),g("img",x({key:3,src:a.image,alt:a.ariaLabel,onError:t[0]||(t[0]=function(){return v.onError&&v.onError.apply(v,arguments)})},a.ptm("image"),{"data-p":v.dataP}),null,16,da)):P("",!0)]})],16,la)}B.render=pa;const ca={key:0,class:"detail-view"},ua={class:"detail-header"},va={class:"header-left"},ma={class:"detail-title"},fa={class:"detail-loc"},ga={class:"header-right"},ha={class:"big-score"},ba={class:"detail-grid"},ya={class:"field-label"},_a={class:"field-value"},wa={class:"dim-name-cell"},xa={class:"dim-score-bar"},za={class:"dim-score-val"},ka={class:"reasoning-text"},Sa={key:1,class:"empty-detail"},$a={__name:"CandidateDetailView",setup(a){const t=Q(),c=J(),h=H(),s=f(()=>h.getCandidate(t.params.id)),v=f(()=>{var e;const i=((e=s.value)==null?void 0:e.rank)||0;return i<=10?"danger":i<=30?"warn":i<=60?"info":"contrast"}),E=f(()=>{const i=s.value;if(!i)return[];const e=i.profile||{};return[{label:"Name",value:e.anonymized_name||"-"},{label:"Current Title",value:i.current_title||"-"},{label:"Company",value:i.current_company||"-"},{label:"Location",value:[e.location,e.country].filter(Boolean).join(", ")||"-"},{label:"Years of Exp",value:e.years_of_experience??"-"},{label:"Industry",value:e.current_industry||"-"},{label:"Company Size",value:e.current_company_size||"-"},{label:"Headline",value:(e.headline||"").slice(0,80)||"-"}]}),F={title_role:"pi pi-id-card",skills:"pi pi-cog",career_quality:"pi pi-building",experience:"pi pi-clock",statement:"pi pi-pen",behavioral:"pi pi-heart",location:"pi pi-map-marker",education:"pi pi-book"},_=f(()=>{const i=s.value;return!i||!h.weights?[]:Object.entries(h.weights).map(([e,k])=>{var n;return{key:e,label:e.replace(/_/g," ").replace(/\b\w/g,w=>w.toUpperCase()),icon:F[e]||"pi pi-circle",score:i.sub_scores[e]||0,weight:k,reasoning:((n=i.reasonings)==null?void 0:n[e])||""}})}),R=f(()=>_.value.map(i=>i.label)),j=f(()=>_.value.map(i=>i.score)),L=f(()=>_.value.map(i=>i.weight)),D=f(()=>[{name:"Score",data:j.value},{name:"Weight",data:L.value}]),V={chart:{type:"radar",toolbar:{show:!1},fontFamily:"Inter"},colors:["#00bcd4","#ff9800"],xaxis:{categories:R.value,labels:{style:{colors:"#e4e6f0"}}},yaxis:{show:!1,min:0,max:1},markers:{size:5},stroke:{width:2},fill:{opacity:.1},tooltip:{theme:"dark"},legend:{labels:{colors:"#e4e6f0"}}};return(i,e)=>{const k=M("apexchart");return s.value?(u(),g("div",ca,[o(l(T),{icon:"pi pi-arrow-left",text:"",onClick:e[0]||(e[0]=n=>l(c).push("/results")),label:"Back to Results",class:"back-btn"}),o(l(z),{class:"detail-header-card"},{content:p(()=>{var n,w;return[r("div",ua,[r("div",va,[o(l(B),{label:((n=s.value.name)==null?void 0:n[0])||"?",shape:"circle",size:"xlarge",style:{background:"var(--p-primary-500)",color:"#fff"}},null,8,["label"]),r("div",null,[r("h2",null,d(s.value.candidate_id),1),r("p",ma,[m(d(s.value.current_title)+" ",1),e[1]||(e[1]=r("span",{class:"at-text"},"at",-1)),m(" "+d(s.value.current_company),1)]),r("p",fa,[e[2]||(e[2]=r("i",{class:"pi pi-map-marker"},null,-1)),m(" "+d(s.value.location),1)])])]),r("div",ga,[o(l(q),{value:`Rank #${s.value.rank}`,severity:v.value,size:"large"},null,8,["value","severity"]),r("div",ha,d(s.value.score.toFixed(4)),1),e[3]||(e[3]=r("span",{class:"score-label"},"Overall Score",-1))])]),(w=s.value.honeypot)!=null&&w.is_honeypot?(u(),$(l(G),{key:0,severity:"warn",closable:!1,class:"honey-msg"},{default:p(()=>[e[4]||(e[4]=r("i",{class:"pi pi-exclamation-triangle"},null,-1)),m(" Honeypot detected: "+d(s.value.honeypot.flags.join(", "))+" — Penalty: "+d((s.value.honeypot.penalty*100).toFixed(0))+"% ",1)]),_:1})):P("",!0)]}),_:1}),r("div",ba,[o(l(z),null,{title:p(()=>[...e[5]||(e[5]=[r("i",{class:"pi pi-user"},null,-1),m(" Profile Summary",-1)])]),content:p(()=>[(u(!0),g(K,null,U(E.value,n=>(u(),g("div",{class:"profile-field",key:n.label},[r("span",ya,d(n.label),1),r("span",_a,d(n.value),1)]))),128))]),_:1}),o(l(z),null,{title:p(()=>[...e[6]||(e[6]=[r("i",{class:"pi pi-chart-pie"},null,-1),m(" Scores vs Weights",-1)])]),content:p(()=>[o(k,{type:"radar",height:"340",options:V,series:D.value},null,8,["series"])]),_:1})]),o(l(z),null,{title:p(()=>[...e[7]||(e[7]=[r("i",{class:"pi pi-table"},null,-1),m(" Dimension Breakdown",-1)])]),content:p(()=>[o(l(X),{value:_.value,stripedRows:"",showGridlines:"",class:"dims-table"},{default:p(()=>[o(l(b),{field:"label",header:"Dimension"},{body:p(({data:n})=>[r("div",wa,[r("i",{class:C(n.icon)},null,2),m(" "+d(n.label),1)])]),_:1}),o(l(b),{field:"score",header:"Score",style:{width:"160px"}},{body:p(({data:n})=>[r("div",xa,[o(l(Y),{value:n.score*100,showValue:!1},null,8,["value"]),r("span",za,d(n.score.toFixed(3)),1)])]),_:1}),o(l(b),{field:"weight",header:"Weight",style:{width:"70px"}},{body:p(({data:n})=>[m(d(n.weight.toFixed(2)),1)]),_:1}),o(l(b),{field:"weighted",header:"Weighted",style:{width:"90px"}},{body:p(({data:n})=>[r("strong",null,d((n.score*n.weight).toFixed(4)),1)]),_:1}),o(l(b),{field:"reasoning",header:"Reasoning"},{body:p(({data:n})=>[r("span",ka,d(n.reasoning),1)]),_:1})]),_:1},8,["value"])]),_:1})])):(u(),g("div",Sa,[...e[8]||(e[8]=[r("i",{class:"pi pi-spin pi-spinner",style:{"font-size":"2rem"}},null,-1),r("p",null,"Candidate not found",-1)])]))}}},Fa=Z($a,[["__scopeId","data-v-ab2312bf"]]);export{Fa as default};
