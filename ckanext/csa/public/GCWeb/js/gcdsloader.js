
/**
 * @title GCDS loader
 * @overview Script to load GCDS which was tested for co-existance in GCWeb
 * @license wet-boew.github.io/wet-boew/License-en.html / wet-boew.github.io/wet-boew/Licence-fr.html
 * @author @duboisp
 */
( function( wnd, doc, escape ) {
"use strict";


//
// Configuration updated during the build process with info in package.json
//
const gcdsVersion = "0.43.1", // pkg.peerDependencies[ "@cdssnc/gcds-components" ]
	gcdsSriJs = "sha384-LvlLD5RBuKfWk4D3tLBoQb10idfyXY2NzeDN/WylPZcZm1mWEvAAUvtaBOrq3Aw5", // pkg[ "io.github.wet-boew" ].gcdsSriJs
	gcdsSriCss = "sha384-nbfuI8ypmBcicF3iEfQgDR5GbezYoSB81DQu2M3imy8Cp5ynFJWqdJ64Qond1esU"; // pkg[ "io.github.wet-boew" ].gcdsSriCss


//
// General configuration used to detect and load GCSD
//
const gcdsBasePath = "https://cdn.design-system.alpha.canada.ca/@cdssnc/gcds-components@",
	gcdsSuffixJs = "/dist/gcds/gcds.esm.js",
	gcdsSuffixCss = "/dist/gcds/gcds.css",
	txtScript = "script",
	txtLink = "link",
	blockingState = "render";


//
// Check if GCDS lib are already defined in the header
//
let traceFound = doc.querySelector( txtLink + "[href$=" + escape( gcdsSuffixCss ) + "]," + txtScript + "[src$=" + escape( gcdsSuffixJs ) + "]" );


//
// Import the GCDS libs
//
if ( !traceFound && gcdsSriJs && gcdsSriCss ) {
	let scrGcds = doc.createElement( txtScript );
	scrGcds.blocking = blockingState;
	scrGcds.type = "module";
	scrGcds.integrity = gcdsSriJs;
	scrGcds.src = gcdsBasePath + gcdsVersion + gcdsSuffixJs;
	doc.head.appendChild( scrGcds );

	let lnkGcds = doc.createElement( txtLink );
	lnkGcds.blocking = blockingState;
	lnkGcds.rel = "stylesheet";
	lnkGcds.crossOrigin = "anonymous";
	lnkGcds.integrity = gcdsSriCss;
	lnkGcds.href = gcdsBasePath + gcdsVersion + gcdsSuffixCss;
	doc.head.appendChild( lnkGcds );


	//
	// Set GCDS version globally once loaded
	//
	wnd.addEventListener( "appload", ( event ) => {
		if ( event.detail.namespace === "gcds" ) {
			wnd.wbgcds = gcdsVersion;
		}
	} );
}

} )( window, document, CSS.escape );
