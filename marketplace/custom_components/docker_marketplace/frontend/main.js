function t(t,e,i,s){var o,a=arguments.length,r=a<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)r=Reflect.decorate(t,e,i,s);else for(var n=t.length-1;n>=0;n--)(o=t[n])&&(r=(a<3?o(r):a>3?o(e,i,r):o(e,i))||r);return a>3&&r&&Object.defineProperty(e,i,r),r}"function"==typeof SuppressedError&&SuppressedError;
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const e=globalThis,i=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),o=new WeakMap;let a=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(i&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=o.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&o.set(e,t))}return t}toString(){return this.cssText}};const r=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new a(i,t,s)},n=i?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new a("string"==typeof t?t:t+"",void 0,s))(e)})(t):t,{is:l,defineProperty:c,getOwnPropertyDescriptor:d,getOwnPropertyNames:p,getOwnPropertySymbols:h,getPrototypeOf:g}=Object,u=globalThis,v=u.trustedTypes,f=v?v.emptyScript:"",m=u.reactiveElementPolyfillSupport,_=(t,e)=>t,y={toAttribute(t,e){switch(e){case Boolean:t=t?f:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},b=(t,e)=>!l(t,e),x={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:b};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */Symbol.metadata??=Symbol("metadata"),u.litPropertyMetadata??=new WeakMap;let $=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=x){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&c(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:o}=d(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const a=s?.call(this);o?.call(this,e),this.requestUpdate(t,a,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??x}static _$Ei(){if(this.hasOwnProperty(_("elementProperties")))return;const t=g(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(_("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(_("properties"))){const t=this.properties,e=[...p(t),...h(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,s)=>{if(i)t.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of s){const s=document.createElement("style"),o=e.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=i.cssText,t.appendChild(s)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const o=(void 0!==i.converter?.toAttribute?i.converter:y).toAttribute(e,i.type);this._$Em=t,null==o?this.removeAttribute(s):this.setAttribute(s,o),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),o="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:y;this._$Em=s;const a=o.fromAttribute(e,t.type);this[s]=a??this._$Ej?.get(s)??a,this._$Em=null}}requestUpdate(t,e,i){if(void 0!==t){const s=this.constructor,o=this[t];if(i??=s.getPropertyOptions(t),!((i.hasChanged??b)(o,e)||i.useDefault&&i.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(s._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:o},a){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,a??e??this[t]),!0!==o||void 0!==a)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[_("elementProperties")]=new Map,$[_("finalized")]=new Map,m?.({ReactiveElement:$}),(u.reactiveElementVersions??=[]).push("2.1.1");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const A=globalThis,w=A.trustedTypes,C=w?w.createPolicy("lit-html",{createHTML:t=>t}):void 0,k="$lit$",S=`lit$${Math.random().toFixed(9).slice(2)}$`,E="?"+S,P=`<${E}>`,z=document,M=()=>z.createComment(""),I=t=>null===t||"object"!=typeof t&&"function"!=typeof t,O=Array.isArray,U="[ \t\n\f\r]",R=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,T=/-->/g,D=/>/g,H=RegExp(`>|${U}(?:([^\\s"'>=/]+)(${U}*=${U}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),N=/'/g,j=/"/g,q=/^(?:script|style|textarea|title)$/i,L=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),F=Symbol.for("lit-noChange"),B=Symbol.for("lit-nothing"),V=new WeakMap,W=z.createTreeWalker(z,129);function Q(t,e){if(!O(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==C?C.createHTML(e):e}const G=(t,e)=>{const i=t.length-1,s=[];let o,a=2===e?"<svg>":3===e?"<math>":"",r=R;for(let e=0;e<i;e++){const i=t[e];let n,l,c=-1,d=0;for(;d<i.length&&(r.lastIndex=d,l=r.exec(i),null!==l);)d=r.lastIndex,r===R?"!--"===l[1]?r=T:void 0!==l[1]?r=D:void 0!==l[2]?(q.test(l[2])&&(o=RegExp("</"+l[2],"g")),r=H):void 0!==l[3]&&(r=H):r===H?">"===l[0]?(r=o??R,c=-1):void 0===l[1]?c=-2:(c=r.lastIndex-l[2].length,n=l[1],r=void 0===l[3]?H:'"'===l[3]?j:N):r===j||r===N?r=H:r===T||r===D?r=R:(r=H,o=void 0);const p=r===H&&t[e+1].startsWith("/>")?" ":"";a+=r===R?i+P:c>=0?(s.push(n),i.slice(0,c)+k+i.slice(c)+S+p):i+S+(-2===c?e:p)}return[Q(t,a+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]};class J{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let o=0,a=0;const r=t.length-1,n=this.parts,[l,c]=G(t,e);if(this.el=J.createElement(l,i),W.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=W.nextNode())&&n.length<r;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(k)){const e=c[a++],i=s.getAttribute(t).split(S),r=/([.?@])?(.*)/.exec(e);n.push({type:1,index:o,name:r[2],strings:i,ctor:"."===r[1]?tt:"?"===r[1]?et:"@"===r[1]?it:Y}),s.removeAttribute(t)}else t.startsWith(S)&&(n.push({type:6,index:o}),s.removeAttribute(t));if(q.test(s.tagName)){const t=s.textContent.split(S),e=t.length-1;if(e>0){s.textContent=w?w.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],M()),W.nextNode(),n.push({type:2,index:++o});s.append(t[e],M())}}}else if(8===s.nodeType)if(s.data===E)n.push({type:2,index:o});else{let t=-1;for(;-1!==(t=s.data.indexOf(S,t+1));)n.push({type:7,index:o}),t+=S.length-1}o++}}static createElement(t,e){const i=z.createElement("template");return i.innerHTML=t,i}}function K(t,e,i=t,s){if(e===F)return e;let o=void 0!==s?i._$Co?.[s]:i._$Cl;const a=I(e)?void 0:e._$litDirective$;return o?.constructor!==a&&(o?._$AO?.(!1),void 0===a?o=void 0:(o=new a(t),o._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=o:i._$Cl=o),void 0!==o&&(e=K(t,o._$AS(t,e.values),o,s)),e}class Z{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??z).importNode(e,!0);W.currentNode=s;let o=W.nextNode(),a=0,r=0,n=i[0];for(;void 0!==n;){if(a===n.index){let e;2===n.type?e=new X(o,o.nextSibling,this,t):1===n.type?e=new n.ctor(o,n.name,n.strings,this,t):6===n.type&&(e=new st(o,this,t)),this._$AV.push(e),n=i[++r]}a!==n?.index&&(o=W.nextNode(),a++)}return W.currentNode=z,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class X{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=B,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=K(this,t,e),I(t)?t===B||null==t||""===t?(this._$AH!==B&&this._$AR(),this._$AH=B):t!==this._$AH&&t!==F&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>O(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==B&&I(this._$AH)?this._$AA.nextSibling.data=t:this.T(z.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=J.createElement(Q(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new Z(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=V.get(t.strings);return void 0===e&&V.set(t.strings,e=new J(t)),e}k(t){O(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const o of t)s===e.length?e.push(i=new X(this.O(M()),this.O(M()),this,this.options)):i=e[s],i._$AI(o),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class Y{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,o){this.type=1,this._$AH=B,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=B}_$AI(t,e=this,i,s){const o=this.strings;let a=!1;if(void 0===o)t=K(this,t,e,0),a=!I(t)||t!==this._$AH&&t!==F,a&&(this._$AH=t);else{const s=t;let r,n;for(t=o[0],r=0;r<o.length-1;r++)n=K(this,s[i+r],e,r),n===F&&(n=this._$AH[r]),a||=!I(n)||n!==this._$AH[r],n===B?t=B:t!==B&&(t+=(n??"")+o[r+1]),this._$AH[r]=n}a&&!s&&this.j(t)}j(t){t===B?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class tt extends Y{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===B?void 0:t}}class et extends Y{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==B)}}class it extends Y{constructor(t,e,i,s,o){super(t,e,i,s,o),this.type=5}_$AI(t,e=this){if((t=K(this,t,e,0)??B)===F)return;const i=this._$AH,s=t===B&&i!==B||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==B&&(i===B||s);s&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class st{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){K(this,t)}}const ot=A.litHtmlPolyfillSupport;ot?.(J,X),(A.litHtmlVersions??=[]).push("3.3.1");const at=globalThis;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */class rt extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let o=s._$litPart$;if(void 0===o){const t=i?.renderBefore??null;s._$litPart$=o=new X(e.insertBefore(M(),t),t,void 0,i??{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return F}}rt._$litElement$=!0,rt.finalized=!0,at.litElementHydrateSupport?.({LitElement:rt});const nt=at.litElementPolyfillSupport;nt?.({LitElement:rt}),(at.litElementVersions??=[]).push("4.2.1");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const lt=t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},ct={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:b},dt=(t=ct,e,i)=>{const{kind:s,metadata:o}=i;let a=globalThis.litPropertyMetadata.get(o);if(void 0===a&&globalThis.litPropertyMetadata.set(o,a=new Map),"setter"===s&&((t=Object.create(t)).wrapped=!0),a.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const o=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,o,t)},init(e){return void 0!==e&&this.C(s,void 0,t,e),e}}}if("setter"===s){const{name:s}=i;return function(i){const o=this[s];e.call(this,i),this.requestUpdate(s,o,t)}}throw Error("Unsupported decorator location: "+s)};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function pt(t){return(e,i)=>"object"==typeof i?dt(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function ht(t){return pt({...t,state:!0,attribute:!1})}class gt{constructor(t){this.hass=t}async getCatalog(){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/catalog"})}async getInstalled(){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/installed"})}async getAppStatus(t){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/app_status",app_id:t})}async installApp(t,e){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/install",app_id:t,config:e||{}})}async removeApp(t,e=!1){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/remove",app_id:t,remove_data:e})}async getLogs(t,e=100){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/logs",app_id:t,tail:e})}async startApp(t){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/start",app_id:t})}async stopApp(t){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/stop",app_id:t})}async restartApp(t){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/restart",app_id:t})}async updateApp(t){return this.hass.callService("docker_marketplace","update_app",{app_id:t})}async getConfig(t){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/get_config",app_id:t})}async updateConfig(t,e){return this.hass.connection.sendMessagePromise({type:"docker_marketplace/update_config",app_id:t,config:e})}}let ut=class extends rt{constructor(){super(...arguments),this.categories=[],this.selected="all"}render(){return L`
      <div class="filter-container">
        <button
          class="filter-chip ${"all"===this.selected?"selected":""}"
          @click=${()=>this._selectCategory("all")}
        >
          <ha-icon icon="mdi:view-grid"></ha-icon>
          Tout
        </button>

        <button
          class="filter-chip ${"installed"===this.selected?"selected":""}"
          @click=${()=>this._selectCategory("installed")}
        >
          <ha-icon icon="mdi:check-circle"></ha-icon>
          Installées
        </button>

        ${this.categories.map(t=>L`
            <button
              class="filter-chip ${this.selected===t.id?"selected":""}"
              @click=${()=>this._selectCategory(t.id)}
            >
              <ha-icon .icon=${t.icon}></ha-icon>
              ${t.name}
              <span class="count">${t.app_count}</span>
            </button>
          `)}
      </div>
    `}_selectCategory(t){this.selected=t,this.dispatchEvent(new CustomEvent("category-change",{detail:{category:t},bubbles:!0,composed:!0}))}};ut.styles=r`
    :host {
      display: block;
    }

    .filter-container {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 4px 0;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }

    .filter-container::-webkit-scrollbar {
      display: none;
    }

    .filter-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 18px;
      background: var(--card-background-color);
      border: 1px solid var(--divider-color);
      color: var(--primary-text-color);
      font-size: 14px;
      font-weight: 400;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
      user-select: none;
    }

    .filter-chip:hover {
      background: var(--secondary-background-color);
    }

    .filter-chip.selected {
      background: var(--primary-color);
      border-color: var(--primary-color);
      color: var(--text-primary-color, #fff);
    }

    .filter-chip ha-icon {
      --mdc-icon-size: 18px;
    }

    .filter-chip.selected ha-icon {
      color: var(--text-primary-color, #fff);
    }

    .count {
      font-size: 12px;
      opacity: 0.7;
      margin-left: 2px;
    }
  `,t([pt({type:Array})],ut.prototype,"categories",void 0),t([pt({type:String})],ut.prototype,"selected",void 0),ut=t([lt("category-filter")],ut);let vt=class extends rt{render(){if(!this.app&&!this.installed)return L``;const t=this.app?.name||this.installed?.name||"Unknown",e=this.app?.description||"",i=this.app?.version||this.installed?.version||"",s=this.app?.icon||"mdi:docker",o=this.installed?.state;return L`
      <ha-card @click=${this._handleClick}>
        <div class="card-content">
          <div class="header">
            <div class="icon-container">
              <ha-icon .icon=${s}></ha-icon>
            </div>
            <div class="info">
              <h3 class="name">${t}</h3>
              <span class="version">v${i}</span>
            </div>
          </div>

          ${e?L`<p class="description">${e}</p>`:""}

          <div class="footer">
            ${o?this._renderStatus(o):L`<span class="category-badge">${this.app?.category||""}</span>`}
            ${this.installed&&"running"===o?this._renderStats():""}
          </div>
        </div>
      </ha-card>
    `}_renderStatus(t){return L`
      <span class="status">
        <span class="status-dot ${t}"></span>
        ${{running:"En cours",stopped:"Arrêté",installing:"Installation...",error:"Erreur",not_installed:"Non installé"}[t]||t}
      </span>
    `}_renderStats(){return this.installed?L`
      <div class="stats">
        <div class="stat">
          <ha-icon icon="mdi:cpu-64-bit"></ha-icon>
          ${this.installed.cpu_percent.toFixed(1)}%
        </div>
        <div class="stat">
          <ha-icon icon="mdi:memory"></ha-icon>
          ${this._formatMemory(this.installed.memory_usage)}
        </div>
      </div>
    `:""}_formatMemory(t){return t<1048576?`${(t/1024).toFixed(0)} KB`:t<1073741824?`${(t/1048576).toFixed(0)} MB`:`${(t/1073741824).toFixed(1)} GB`}_handleClick(){this.dispatchEvent(new CustomEvent("app-click",{detail:{app:this.app,installed:this.installed},bubbles:!0,composed:!0}))}};vt.styles=r`
    :host {
      display: block;
    }

    ha-card {
      cursor: pointer;
      height: 100%;
      transition: box-shadow 0.2s ease-in-out;
    }

    ha-card:hover {
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
    }

    .card-content {
      padding: 16px;
    }

    .header {
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }

    .icon-container {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: var(--primary-color);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .icon-container ha-icon {
      color: white;
      --mdc-icon-size: 24px;
    }

    .info {
      flex: 1;
      min-width: 0;
    }

    .name {
      font-size: 16px;
      font-weight: 500;
      color: var(--primary-text-color);
      margin: 0 0 4px 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .version {
      font-size: 12px;
      color: var(--secondary-text-color);
    }

    .description {
      font-size: 14px;
      color: var(--secondary-text-color);
      margin: 12px 0 0 0;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--divider-color);
    }

    .status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 500;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    .status-dot.running {
      background: var(--success-color, #4caf50);
    }

    .status-dot.stopped {
      background: var(--error-color, #f44336);
    }

    .status-dot.installing {
      background: var(--warning-color, #ff9800);
    }

    .status-dot.error {
      background: var(--error-color, #f44336);
    }

    .stats {
      display: flex;
      gap: 12px;
      font-size: 12px;
      color: var(--secondary-text-color);
    }

    .stat {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .stat ha-icon {
      --mdc-icon-size: 14px;
    }

    .category-badge {
      font-size: 11px;
      color: var(--secondary-text-color);
      background: var(--secondary-background-color);
      padding: 4px 8px;
      border-radius: 4px;
      text-transform: capitalize;
    }
  `,t([pt({type:Object})],vt.prototype,"app",void 0),t([pt({type:Object})],vt.prototype,"installed",void 0),vt=t([lt("app-card")],vt);let ft=class extends rt{constructor(){super(...arguments),this.open=!1,this.loading=!1,this._config={},this._savedConfig={},this._configSchema=null,this._activeTab="status",this._confirmDelete=!1,this._configLoading=!1,this._configDirty=!1,this._savingConfig=!1}updated(t){t.has("hass")&&this.hass&&!this._api&&(this._api=new gt(this.hass)),t.has("open")&&this.open&&this.installed&&this._loadConfig()}async _loadConfig(){if(this._api&&this.app?.id){this._configLoading=!0;try{const t=await this._api.getConfig(this.app.id);this._savedConfig=t.config||{},this._config={...this._savedConfig},this._configSchema=t.schema,this._configDirty=!1}catch(t){console.error("Failed to load config:",t)}finally{this._configLoading=!1}}}render(){return this.app?L`
      <ha-dialog
        ?open=${this.open}
        @closed=${this._handleClose}
        hideActions
      >
        <div class="dialog-content">
          ${this.loading?L`
                <div class="loading-overlay">
                  <ha-circular-progress indeterminate></ha-circular-progress>
                  <span>Installation en cours...</span>
                </div>
              `:""}

          <div class="header">
            <div class="icon-container">
              <ha-icon .icon=${this.app.icon||"mdi:docker"}></ha-icon>
            </div>
            <div class="title-section">
              <h2 class="app-name">${this.app.name}</h2>
              <div class="app-meta">
                <span>v${this.app.version}</span>
                ${this.installed?L`
                      <span class="status-indicator ${this.installed.state}">
                        ${this._getStatusLabel(this.installed.state)}
                      </span>
                    `:""}
              </div>
            </div>
          </div>

          <p class="description">${this.app.description}</p>

          ${this._confirmDelete?this._renderConfirmDelete():""}

          ${this.installed?this._renderInstalledTabs():this._renderInstall()}

          ${this._confirmDelete?"":this._renderActions()}
        </div>
      </ha-dialog>
    `:L``}_renderConfirmDelete(){return L`
      <div class="confirm-delete">
        <div class="confirm-delete-title">
          <ha-icon icon="mdi:alert"></ha-icon>
          Confirmer la suppression
        </div>
        <div class="confirm-delete-text">
          Êtes-vous sûr de vouloir supprimer <strong>${this.app?.name}</strong> ?
          Cette action est irréversible.
        </div>
        <div class="confirm-delete-actions">
          <ha-button @click=${()=>this._confirmDelete=!1}>Annuler</ha-button>
          <ha-button class="danger-btn" @click=${this._confirmRemove}>Supprimer</ha-button>
        </div>
      </div>
    `}_renderInstalledTabs(){return L`
      <div class="tab-bar">
        <button
          class="tab-button ${"status"===this._activeTab?"active":""}"
          @click=${()=>this._activeTab="status"}
        >
          Statut
        </button>
        <button
          class="tab-button ${"config"===this._activeTab?"active":""}"
          @click=${()=>this._activeTab="config"}
        >
          Configuration
        </button>
      </div>
      <div class="tab-content">
        ${"status"===this._activeTab?this._renderInstalled():this._renderConfigTab()}
      </div>
    `}_renderConfigTab(){if(this._configLoading)return L`
        <div class="loading-container" style="padding: 40px; text-align: center;">
          <ha-circular-progress indeterminate></ha-circular-progress>
          <p style="margin-top: 16px; color: var(--secondary-text-color);">Chargement de la configuration...</p>
        </div>
      `;if(!this._configSchema)return L`
        <div class="section">
          <p style="color: var(--secondary-text-color); font-size: 13px;">
            Aucune configuration disponible pour cette application.
          </p>
        </div>
      `;const t=this._configSchema.ports.length>0,e=this._configSchema.volumes.length>0,i=this._configSchema.environment.length>0;return t||e||i?L`
      ${this._configDirty?L`
            <div class="config-message">
              <ha-icon icon="mdi:alert-circle"></ha-icon>
              Des modifications non enregistrées. Redémarrez l'application après sauvegarde.
            </div>
          `:""}

      ${t?L`
            <div class="section">
              <div class="section-title">Ports</div>
              ${this._configSchema.ports.map(t=>L`
                  <div class="field">
                    <label class="field-label">${t.description||`Port ${t.container}`}</label>
                    <ha-textfield
                      type="number"
                      .value=${String(this._config[t.key]??t.host)}
                      @input=${e=>this._updateConfigField(t.key,e.target.value)}
                    ></ha-textfield>
                    <span class="field-hint">Port conteneur: ${t.container}/${t.protocol}</span>
                  </div>
                `)}
            </div>
          `:""}

      ${e?L`
            <div class="section">
              <div class="section-title">Volumes</div>
              ${this._configSchema.volumes.map(t=>L`
                  <div class="field">
                    <label class="field-label">
                      ${t.description||t.name}
                      ${t.required?L`<span style="color: var(--error-color)">*</span>`:""}
                    </label>
                    <ha-textfield
                      .value=${String(this._config[t.key]??t.default_host??"")}
                      @input=${e=>this._updateConfigField(t.key,e.target.value)}
                    ></ha-textfield>
                    <span class="field-hint">Chemin conteneur: ${t.container}</span>
                  </div>
                `)}
            </div>
          `:""}

      ${i?L`
            <div class="section">
              <div class="section-title">Variables d'environnement</div>
              ${this._configSchema.environment.map(t=>L`
                  <div class="field">
                    <label class="field-label">
                      ${t.description||t.name}
                      ${t.required?L`<span style="color: var(--error-color)">*</span>`:""}
                    </label>
                    <ha-textfield
                      .type=${t.secret?"password":"text"}
                      .value=${String(this._config[t.key]??t.default??"")}
                      @input=${e=>this._updateConfigField(t.key,e.target.value)}
                    ></ha-textfield>
                  </div>
                `)}
            </div>
          `:""}

      ${this._configDirty?L`
            <div class="config-actions">
              <ha-button @click=${this._resetConfig}>Annuler</ha-button>
              <ha-button unelevated ?disabled=${this._savingConfig} @click=${this._saveConfig}>
                ${this._savingConfig?"Enregistrement...":"Enregistrer"}
              </ha-button>
            </div>
          `:""}
    `:L`
        <div class="section">
          <p style="color: var(--secondary-text-color); font-size: 13px;">
            Cette application utilise la configuration par défaut.
          </p>
        </div>
      `}_updateConfigField(t,e){this._config={...this._config,[t]:e},this._configDirty=JSON.stringify(this._config)!==JSON.stringify(this._savedConfig)}_resetConfig(){this._config={...this._savedConfig},this._configDirty=!1}async _saveConfig(){if(this._api&&this.app?.id){this._savingConfig=!0;try{await this._api.updateConfig(this.app.id,this._config),this._savedConfig={...this._config},this._configDirty=!1}catch(t){console.error("Failed to save config:",t)}finally{this._savingConfig=!1}}}_renderInstalled(){return this.installed?L`
      <div class="section">
        <div class="section-title">Statut</div>
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">État</div>
            <div class="info-value">${this._getStatusLabel(this.installed.state)}</div>
          </div>
          <div class="info-item">
            <div class="info-label">Image</div>
            <div class="info-value">${this.installed.image}</div>
          </div>
          ${"running"===this.installed.state?L`
                <div class="info-item">
                  <div class="info-label">CPU</div>
                  <div class="info-value">${this.installed.cpu_percent.toFixed(1)}%</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Mémoire</div>
                  <div class="info-value">${this._formatMemory(this.installed.memory_usage)}</div>
                </div>
              `:""}
        </div>
      </div>
    `:""}_renderInstall(){const t=(this.app?.ports?.length||0)>0,e=(this.app?.environment?.length||0)>0,i=this.app?.requirements?.min_memory||"none"!==this.app?.requirements?.gpu,s=this.app?.environment?.filter(t=>t.required).length||0;return t||e?L`
      ${s>0?L`
            <div class="required-notice">
              <ha-icon icon="mdi:alert-circle"></ha-icon>
              <span>${s} champ(s) requis pour l'installation</span>
            </div>
          `:""}

      ${s>0?L`
            <div class="section">
              <div class="section-title">Configuration</div>
              ${this.app.environment.filter(t=>t.required).map(t=>L`
                  <div class="field">
                    <label class="field-label">
                      ${t.description||t.name}
                    </label>
                    <ha-textfield
                      .type=${t.secret?"password":"text"}
                      .value=${String(this._config[`env_${t.name}`]??t.default??"")}
                      required
                      @input=${e=>this._updateConfig(`env_${t.name}`,e.target.value)}
                    ></ha-textfield>
                  </div>
                `)}
            </div>
          `:""}

      ${t?L`
            <div class="section">
              <div class="section-title">Ports</div>
              ${this.app.ports.map(t=>L`
                  <div class="field">
                    <label class="field-label">${t.description||`Port ${t.container}`}</label>
                    <ha-textfield
                      type="number"
                      .value=${String(this._config[`port_${t.container}`]||t.host)}
                      @input=${e=>this._updateConfig(`port_${t.container}`,e.target.value)}
                    ></ha-textfield>
                    <span class="field-hint">Port conteneur: ${t.container}/${t.protocol}</span>
                  </div>
                `)}
            </div>
          `:""}

      ${i?L`
            <div class="section">
              <div class="section-title">Prérequis</div>
              <div class="requirements-grid">
                ${this.app.requirements.min_memory?L`
                      <div class="requirement">
                        <ha-icon icon="mdi:memory"></ha-icon>
                        Min ${this.app.requirements.min_memory} MB RAM
                      </div>
                    `:""}
                ${"none"!==this.app.requirements.gpu?L`
                      <div class="requirement">
                        <ha-icon icon="mdi:expansion-card"></ha-icon>
                        GPU ${"required"===this.app.requirements.gpu?"requis":"optionnel"}
                      </div>
                    `:""}
              </div>
            </div>
          `:""}
    `:L`
        <div class="section">
          <p style="color: var(--secondary-text-color)">
            Cette application utilise la configuration par défaut.
          </p>
        </div>
      `}_renderActions(){if(this.installed){const t="running"===this.installed.state;return L`
        <div class="actions">
          <ha-button @click=${this._handleClose}>Fermer</ha-button>
          ${t?L`
                <ha-button @click=${this._handleStop}>Arrêter</ha-button>
                <ha-button @click=${this._handleRestart}>Redémarrer</ha-button>
              `:L`<ha-button unelevated @click=${this._handleStart}>Démarrer</ha-button>`}
          <ha-button class="danger-btn" @click=${this._handleRemove}>Supprimer</ha-button>
        </div>
      `}return L`
      <div class="actions">
        <ha-button @click=${this._handleClose}>Annuler</ha-button>
        <ha-button unelevated ?disabled=${this.loading} @click=${this._handleInstall}>
          ${this.loading?"Installation...":"Installer"}
        </ha-button>
      </div>
    `}_getStatusLabel(t){return{running:"En cours",stopped:"Arrêté",installing:"Installation...",error:"Erreur",not_installed:"Non installé"}[t]||t}_formatMemory(t){return t<1048576?`${(t/1024).toFixed(0)} KB`:t<1073741824?`${(t/1048576).toFixed(0)} MB`:`${(t/1073741824).toFixed(1)} GB`}_updateConfig(t,e){this._config={...this._config,[t]:e}}_handleClose(){this._confirmDelete=!1,this._activeTab="status",this.dispatchEvent(new CustomEvent("dialog-close",{bubbles:!0,composed:!0}))}_handleInstall(){this.dispatchEvent(new CustomEvent("app-install",{detail:{appId:this.app?.id,config:this._config},bubbles:!0,composed:!0}))}_handleStart(){this.dispatchEvent(new CustomEvent("app-start",{detail:{appId:this.app?.id},bubbles:!0,composed:!0}))}_handleStop(){this.dispatchEvent(new CustomEvent("app-stop",{detail:{appId:this.app?.id},bubbles:!0,composed:!0}))}_handleRestart(){this.dispatchEvent(new CustomEvent("app-restart",{detail:{appId:this.app?.id},bubbles:!0,composed:!0}))}_handleRemove(){this._confirmDelete=!0}_confirmRemove(){this._confirmDelete=!1,this.dispatchEvent(new CustomEvent("app-remove",{detail:{appId:this.app?.id},bubbles:!0,composed:!0}))}};ft.styles=r`
    ha-dialog {
      --mdc-dialog-min-width: 500px;
      --mdc-dialog-max-width: 600px;
    }

    .header {
      display: flex;
      align-items: center;
      gap: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 16px;
    }

    .icon-container {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      background: var(--primary-color);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .icon-container ha-icon {
      color: white;
      --mdc-icon-size: 28px;
    }

    .title-section {
      flex: 1;
    }

    .app-name {
      font-size: 20px;
      font-weight: 500;
      color: var(--primary-text-color);
      margin: 0 0 4px 0;
    }

    .app-meta {
      font-size: 13px;
      color: var(--secondary-text-color);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-indicator {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 500;
    }

    .status-indicator.running {
      background: rgba(var(--rgb-green), 0.15);
      color: var(--success-color, #4caf50);
    }

    .status-indicator.stopped {
      background: rgba(var(--rgb-red), 0.15);
      color: var(--error-color, #f44336);
    }

    .description {
      font-size: 14px;
      line-height: 1.5;
      color: var(--primary-text-color);
      margin-bottom: 16px;
    }

    .section {
      margin-bottom: 20px;
    }

    .section-title {
      font-size: 11px;
      font-weight: 600;
      color: var(--secondary-text-color);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
    }

    .info-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }

    .info-item {
      padding: 12px;
      background: var(--secondary-background-color);
      border-radius: 8px;
    }

    .info-label {
      font-size: 11px;
      color: var(--secondary-text-color);
      margin-bottom: 4px;
    }

    .info-value {
      font-size: 14px;
      font-weight: 500;
      color: var(--primary-text-color);
    }

    .field {
      margin-bottom: 16px;
    }

    .field-label {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: var(--primary-text-color);
      margin-bottom: 8px;
    }

    .field-hint {
      font-size: 12px;
      color: var(--secondary-text-color);
      margin-top: 4px;
    }

    .field-required {
      color: var(--error-color);
      font-size: 11px;
      margin-left: 4px;
    }

    .required-notice {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      margin-bottom: 16px;
      background: rgba(var(--rgb-amber), 0.1);
      border-radius: 8px;
      font-size: 13px;
      color: var(--primary-text-color);
    }

    .required-notice ha-icon {
      color: var(--warning-color);
      --mdc-icon-size: 20px;
    }

    ha-textfield {
      display: block;
      width: 100%;
    }

    .actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      padding-top: 16px;
      border-top: 1px solid var(--divider-color);
      margin-top: 16px;
    }

    ha-button {
      --mdc-theme-primary: var(--primary-color);
    }

    .danger-btn {
      --mdc-theme-primary: var(--error-color);
      --ha-label-badge-color: var(--error-color);
    }

    .danger-btn::part(button) {
      color: var(--error-color);
    }

    .tabs {
      display: flex;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 16px;
    }

    .tab {
      padding: 8px 16px;
      font-size: 14px;
      font-weight: 500;
      color: var(--secondary-text-color);
      background: none;
      border: none;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
      transition: color 0.2s, border-color 0.2s;
    }

    .tab:hover {
      color: var(--primary-text-color);
    }

    .tab.active {
      color: var(--primary-color);
      border-bottom-color: var(--primary-color);
    }

    .requirements-grid {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .requirement {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: var(--secondary-background-color);
      border-radius: 8px;
      font-size: 13px;
      color: var(--primary-text-color);
    }

    .requirement ha-icon {
      color: var(--secondary-text-color);
      --mdc-icon-size: 18px;
    }

    .confirm-delete {
      background: rgba(var(--rgb-red), 0.1);
      border: 1px solid var(--error-color);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }

    .confirm-delete-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 500;
      color: var(--error-color);
      margin-bottom: 8px;
    }

    .confirm-delete-title ha-icon {
      --mdc-icon-size: 20px;
    }

    .confirm-delete-text {
      font-size: 13px;
      color: var(--primary-text-color);
      margin-bottom: 12px;
    }

    .confirm-delete-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
    }

    .tab-bar {
      display: flex;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 16px;
    }

    .tab-button {
      padding: 12px 16px;
      font-size: 14px;
      font-weight: 500;
      color: var(--secondary-text-color);
      background: none;
      border: none;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
      transition: color 0.2s, border-color 0.2s;
    }

    .tab-button:hover {
      color: var(--primary-text-color);
    }

    .tab-button.active {
      color: var(--primary-color);
      border-bottom-color: var(--primary-color);
    }

    .tab-content {
      min-height: 150px;
    }

    .config-message {
      padding: 12px;
      background: rgba(var(--rgb-amber), 0.1);
      border-radius: 8px;
      font-size: 13px;
      color: var(--primary-text-color);
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .config-message ha-icon {
      color: var(--warning-color);
      --mdc-icon-size: 20px;
    }

    .config-actions {
      display: flex;
      gap: 8px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid var(--divider-color);
    }

    @media (max-width: 600px) {
      ha-dialog {
        --mdc-dialog-min-width: 90vw;
      }
      .info-grid {
        grid-template-columns: 1fr;
      }
    }

    .loading-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(var(--rgb-card-background-color, 255, 255, 255), 0.9);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 10;
      border-radius: var(--ha-card-border-radius, 12px);
    }

    .loading-overlay span {
      margin-top: 16px;
      font-size: 14px;
      color: var(--primary-text-color);
    }

    .dialog-content {
      position: relative;
    }
  `,t([pt({attribute:!1})],ft.prototype,"hass",void 0),t([pt({type:Object})],ft.prototype,"app",void 0),t([pt({type:Object})],ft.prototype,"installed",void 0),t([pt({type:Boolean})],ft.prototype,"open",void 0),t([pt({type:Boolean})],ft.prototype,"loading",void 0),t([ht()],ft.prototype,"_config",void 0),t([ht()],ft.prototype,"_savedConfig",void 0),t([ht()],ft.prototype,"_configSchema",void 0),t([ht()],ft.prototype,"_activeTab",void 0),t([ht()],ft.prototype,"_confirmDelete",void 0),t([ht()],ft.prototype,"_configLoading",void 0),t([ht()],ft.prototype,"_configDirty",void 0),t([ht()],ft.prototype,"_savingConfig",void 0),ft=t([lt("app-detail-dialog")],ft);let mt=class extends rt{constructor(){super(...arguments),this.narrow=!1,this._loading=!0,this._error="",this._categories=[],this._apps=[],this._installed=[],this._selectedCategory="all",this._searchQuery="",this._selectedApp=null,this._dialogOpen=!1,this._installing=!1}connectedCallback(){super.connectedCallback(),this._refreshInterval=window.setInterval(()=>{this._loadInstalled()},3e4)}disconnectedCallback(){super.disconnectedCallback(),this._refreshInterval&&clearInterval(this._refreshInterval)}updated(t){t.has("hass")&&this.hass&&!this._api&&(this._api=new gt(this.hass),this._loadData())}async _loadData(){this._loading=!0,this._error="";try{const[t,e]=await Promise.all([this._api.getCatalog(),this._api.getInstalled()]);this._categories=t.categories,this._apps=t.apps,this._installed=e.apps}catch(t){console.error("Failed to load marketplace data:",t),this._error="Impossible de charger le catalogue. Vérifiez que l'intégration est configurée."}finally{this._loading=!1}}async _loadInstalled(){if(this._api)try{const t=await this._api.getInstalled();this._installed=t.apps}catch(t){console.error("Failed to refresh installed apps:",t)}}render(){return L`
      ${this._renderHeader()}

      <div class="content">
        ${this._loading?this._renderLoading():this._error?this._renderError():this._renderMain()}
      </div>

      <app-detail-dialog
        .hass=${this.hass}
        .app=${this._selectedApp}
        .installed=${this._getInstalledApp(this._selectedApp?.id)}
        ?open=${this._dialogOpen}
        ?loading=${this._installing}
        @dialog-close=${this._handleDialogClose}
        @app-install=${this._handleAppInstall}
        @app-start=${this._handleAppStart}
        @app-stop=${this._handleAppStop}
        @app-restart=${this._handleAppRestart}
        @app-update=${this._handleAppUpdate}
        @app-remove=${this._handleAppRemove}
      ></app-detail-dialog>
    `}_renderHeader(){return L`
      <div class="header">
        <div class="header-left">
          ${this.narrow?L`
                <ha-icon-button
                  .label=${"Menu"}
                  .path=${"M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"}
                  @click=${this._toggleSidebar}
                ></ha-icon-button>
              `:""}
          <div class="header-title">
            <ha-icon icon="mdi:store"></ha-icon>
            <span>Nivuus Store</span>
          </div>
        </div>

        <div class="search-input">
          <ha-icon icon="mdi:magnify"></ha-icon>
          <input
            type="text"
            placeholder="Rechercher..."
            .value=${this._searchQuery}
            @input=${this._handleSearch}
          />
        </div>
      </div>
    `}_toggleSidebar(){this.dispatchEvent(new CustomEvent("hass-toggle-menu",{bubbles:!0,composed:!0}))}_renderLoading(){return L`
      <div class="loading-container">
        <ha-circular-progress indeterminate></ha-circular-progress>
        <span>Chargement du catalogue...</span>
      </div>
    `}_renderError(){return L`
      <div class="error-container">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <p>${this._error}</p>
        <mwc-button raised @click=${this._loadData}>
          Réessayer
        </mwc-button>
      </div>
    `}_renderMain(){return L`
      ${this._renderStats()}

      <category-filter
        .categories=${this._categories}
        .selected=${this._selectedCategory}
        @category-change=${this._handleCategoryChange}
      ></category-filter>

      ${this._renderGrid()}
    `}_renderStats(){const t=this._installed.filter(t=>"running"===t.state).length,e=this._installed.length,i=this._apps.length;return L`
      <div class="stats-bar">
        <div class="stat-card">
          <div class="stat-icon running">
            <ha-icon icon="mdi:play-circle"></ha-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">${t}</span>
            <span class="stat-label">En cours</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon installed">
            <ha-icon icon="mdi:check-circle"></ha-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">${e}</span>
            <span class="stat-label">Installées</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon available">
            <ha-icon icon="mdi:package-variant"></ha-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">${i}</span>
            <span class="stat-label">Disponibles</span>
          </div>
        </div>
      </div>
    `}_renderGrid(){const t=this._getFilteredApps();return 0===t.length?L`
        <div class="empty-state">
          <ha-icon icon="mdi:package-variant-closed"></ha-icon>
          <span>Aucune application trouvée</span>
        </div>
      `:L`
      <div class="grid">
        ${t.map(t=>L`
            <app-card
              .app=${t}
              .installed=${this._getInstalledApp(t.id)}
              @app-click=${()=>this._handleAppClick(t)}
            ></app-card>
          `)}
      </div>
    `}_getFilteredApps(){let t=[...this._apps];if("installed"===this._selectedCategory){const e=new Set(this._installed.map(t=>t.id));t=t.filter(t=>e.has(t.id))}else"all"!==this._selectedCategory&&(t=t.filter(t=>t.category===this._selectedCategory));if(this._searchQuery){const e=this._searchQuery.toLowerCase();t=t.filter(t=>t.name.toLowerCase().includes(e)||t.description.toLowerCase().includes(e)||t.tags.some(t=>t.toLowerCase().includes(e)))}return t}_getInstalledApp(t){if(t)return this._installed.find(e=>e.id===t)}_handleSearch(t){this._searchQuery=t.target.value}_handleCategoryChange(t){this._selectedCategory=t.detail.category}_handleAppClick(t){this._selectedApp=t,this._dialogOpen=!0}_handleDialogClose(){this._dialogOpen=!1,this._selectedApp=null}async _handleAppInstall(t){const{appId:e,config:i}=t.detail;if(this._api&&e){this._installing=!0;try{await this._api.installApp(e,i),this._handleDialogClose(),await this._loadInstalled()}catch(t){console.error("Failed to install app:",t)}finally{this._installing=!1}}}async _handleAppStart(t){const{appId:e}=t.detail;if(this._api&&e)try{await this._api.startApp(e),await this._loadInstalled()}catch(t){console.error("Failed to start app:",t)}}async _handleAppStop(t){const{appId:e}=t.detail;if(this._api&&e)try{await this._api.stopApp(e),await this._loadInstalled()}catch(t){console.error("Failed to stop app:",t)}}async _handleAppRestart(t){const{appId:e}=t.detail;if(this._api&&e)try{await this._api.restartApp(e),await this._loadInstalled()}catch(t){console.error("Failed to restart app:",t)}}async _handleAppUpdate(t){const{appId:e}=t.detail;if(this._api&&e)try{await this._api.updateApp(e),await this._loadInstalled()}catch(t){console.error("Failed to update app:",t)}}async _handleAppRemove(t){const{appId:e}=t.detail;if(this._api&&e)try{await this._api.removeApp(e),this._handleDialogClose(),await this._loadInstalled()}catch(t){console.error("Failed to remove app:",t)}}};mt.styles=r`
    :host {
      display: block;
      height: 100%;
      background: var(--primary-background-color);
      --app-header-background-color: var(--sidebar-background-color);
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      height: 56px;
      background: var(--app-header-background-color);
      border-bottom: 1px solid var(--divider-color);
      box-sizing: border-box;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .header-left ha-icon-button {
      color: var(--primary-text-color);
    }

    .header-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 20px;
      font-weight: 400;
      color: var(--primary-text-color);
    }

    .header-title ha-icon {
      color: var(--primary-color);
      --mdc-icon-size: 24px;
    }

    .search-input {
      display: flex;
      align-items: center;
      background: var(--card-background-color);
      border: 1px solid var(--divider-color);
      border-radius: 28px;
      padding: 0 16px;
      height: 40px;
      width: 300px;
      box-sizing: border-box;
    }

    .search-input ha-icon {
      color: var(--secondary-text-color);
      --mdc-icon-size: 20px;
      margin-right: 8px;
    }

    .search-input input {
      flex: 1;
      border: none;
      background: transparent;
      font-size: 14px;
      color: var(--primary-text-color);
      outline: none;
    }

    .search-input input::placeholder {
      color: var(--secondary-text-color);
    }

    .content {
      padding: 16px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .stats-bar {
      display: flex;
      gap: 16px;
      margin-bottom: 16px;
    }

    .stat-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;
      background: var(--card-background-color);
      border-radius: var(--ha-card-border-radius, 12px);
      border: 1px solid var(--divider-color);
      min-width: 140px;
    }

    .stat-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      --mdc-icon-size: 20px;
    }

    .stat-icon.running {
      background: rgba(var(--rgb-green), 0.2);
      color: var(--success-color, #4caf50);
    }

    .stat-icon.installed {
      background: rgba(var(--rgb-primary-color), 0.2);
      color: var(--primary-color);
    }

    .stat-icon.available {
      background: rgba(var(--rgb-amber), 0.2);
      color: var(--warning-color, #ff9800);
    }

    .stat-info {
      display: flex;
      flex-direction: column;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 500;
      color: var(--primary-text-color);
      line-height: 1;
    }

    .stat-label {
      font-size: 12px;
      color: var(--secondary-text-color);
      margin-top: 4px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }

    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 16px;
      color: var(--secondary-text-color);
    }

    .loading-container ha-circular-progress {
      margin-bottom: 16px;
    }

    .error-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 16px;
      text-align: center;
    }

    .error-container ha-icon {
      color: var(--error-color);
      --mdc-icon-size: 48px;
      margin-bottom: 16px;
    }

    .error-container p {
      color: var(--secondary-text-color);
      margin: 0 0 16px 0;
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 16px;
      color: var(--secondary-text-color);
    }

    .empty-state ha-icon {
      --mdc-icon-size: 64px;
      opacity: 0.5;
      margin-bottom: 16px;
    }

    mwc-button {
      --mdc-theme-primary: var(--primary-color);
    }

    @media (max-width: 870px) {
      .search-input {
        width: 200px;
      }
      .stats-bar {
        flex-wrap: wrap;
      }
      .stat-card {
        flex: 1;
        min-width: 120px;
      }
    }

    @media (max-width: 600px) {
      .header {
        flex-direction: column;
        height: auto;
        padding: 12px 16px;
        gap: 12px;
      }
      .search-input {
        width: 100%;
      }
      .grid {
        grid-template-columns: 1fr;
      }
    }
  `,t([pt({attribute:!1})],mt.prototype,"hass",void 0),t([pt({type:Boolean})],mt.prototype,"narrow",void 0),t([ht()],mt.prototype,"_loading",void 0),t([ht()],mt.prototype,"_error",void 0),t([ht()],mt.prototype,"_categories",void 0),t([ht()],mt.prototype,"_apps",void 0),t([ht()],mt.prototype,"_installed",void 0),t([ht()],mt.prototype,"_selectedCategory",void 0),t([ht()],mt.prototype,"_searchQuery",void 0),t([ht()],mt.prototype,"_selectedApp",void 0),t([ht()],mt.prototype,"_dialogOpen",void 0),t([ht()],mt.prototype,"_installing",void 0),mt=t([lt("docker-marketplace-panel")],mt);
