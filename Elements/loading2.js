const waveloader = (() => {
    const loaderHTML = `
         <div id="loader" class="center" >
            <div class="spinner">
                <div class="dot" id="dot1"></div>
                <div class="dot" id="dot2"></div>
                <div class="dot" id="dot3"></div>
                <div class="dot" id="dot4"></div>
            </div>
        </div> `

    const loaderCSS = `
    <style id="wave-style">
         .center {
            position: absolute;
            top: 50%;
            left: 50%;
            
        }

        .spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            position: fixed;
        }

        .dot {
            width: 10px;
            height: 10px;
            background-color: black;
            border-radius: 50%;
            margin: 0 5px;
            animation: bounce 0.5s infinite alternate;
        }

        @keyframes bounce {
            0% {
                transform: translateY(0);
            }
            100% {
                transform: translateY(-20px);
            }
        }

        #dot2 {
            animation-delay: 0.1s;
        }

        #dot3 {
            animation-delay: 0.2s;
        }

        #dot4 {
            animation-delay: 0.3s;
        }
    </style>`;

    
    let loader;

    return {
        show: function () {
            if (!document.getElementById("wave-styles")) {
                document.head.insertAdjacentHTML("beforeend", loaderCSS);
            }
            loader = document.createElement("div");
            loader.innerHTML = loaderHTML;
            loader.id = "wave-loader";
            document.body.appendChild(loader);
        },
        hide: function () {
            if (loader) {
                loader.remove();
            }
        }
    };
})();
