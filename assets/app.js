

// app.clientside_callback(
//     """
//     function(relayoutData, Figure) {
//         //console.log(relayoutData);
//         var piczka = relayoutData
//         console.log(typeof relayoutData);

//         for (const key in relayoutData) {
//             if (relayoutData.hasOwnProperty(key)) {
//                 const value = relayoutData[key];
//                 console.log(`Key: ${key}, Value: ${value}`);
//             }
//         }
        
//         if (typeof relayoutData !== 'undefined') {
//             const relayoutJSON = JSON.stringify(piczka, null, 2);

//             //console.log(relayoutJSON);
            
//             console.log(relayoutData["xaxis.range[0]"]);
//             if (typeof relayoutData["xaxis.range[0]"] !== 'undefined') {
//                 console.log(relayoutData["xaxis.range[0]"]);
//                 fromS = new Date(relayoutData["xaxis.range[0]"]).getTime()
//                 toS = new Date(relayoutData["xaxis.range[1]"]).getTime()
//                 console.log(fromS);
//                 console.log(toS);

//                 xD = Figure.data[0].x
//                 yH = Figure.data[0].high
//                 yM = Figure.data[0].low

//                 const yFiltH = xD.reduce(function (pV, cV, cI) {
//                     const sec = new Date(cV).getTime();
//                     if (sec >= fromS && sec <= toS) {
//                         pV.push(yH[cI]);
//                     }
//                     return pV;
//                 }, []);

//                 const yFiltL = xD.reduce(function (pV, cV, cI) {
//                     const sec = new Date(cV).getTime();
//                     if (sec >= fromS && sec <= toS) {
//                         pV.push(yM[cI]); // Assuming yM represents low values
//                     }
//                     return pV;
//                 }, []);

//                 yMax = Math.max.apply(Math, yFiltH)
//                 yMin = Math.min.apply(Math, yFiltL)



//                 Figure.layout.yaxis = {
//                     'range': [yMin, yMax],
//                     'type': 'linear'
//                 }
//                 return {'data': Figure.data, 'layout': Figure.layout};
//             }


//         }
//         return {'data': Figure.data, 'layout': Figure.layout};
//     }
//     """,
//     # Output('output', 'children'),
//     Output('candlestick-chart', 'figure'),
//     Input('candlestick-chart', 'relayoutData'),
//     State('candlestick-chart', 'figure'),
//     prevent_initial_call=True

// )
