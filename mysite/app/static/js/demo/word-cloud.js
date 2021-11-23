// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';


console.log('calling fron word-cloud-area')
$.ajax({
    type: 'GET',
    url: '/word_cloud',
    beforeSend: function () {
      alert('Taking 1 minute to visualize word cloud...')
    },
    complete: function () {
      alert('Finished...')
    },
    success: function (d) {
        // console.log(d.data)
        let words = d.data.split(" ")
        let parsed_words = []
        for (let i=0; i<words.length; i++)
            parsed_words[i] = JSON.parse(words[i])
        // console.log(typeof(words))
        // console.log(words)
        // console.log(typeof(parsed_words))
        console.log(parsed_words)



        // set the dimensions and margins of the graph
        let wrapper_height = $('.wordcloud-wrapper').height(),
            wrapper_width = $('.wordcloud-wrapper').width()
        var margin = {top: 10, right: 10, bottom: 10, left: 10},
            width = wrapper_width - margin.left - margin.right,
            height = wrapper_height - margin.top - margin.bottom;

        // append the svg object to the body of the page
        var svg = d3.select("#wordcloud-chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform",
                  "translate(" + margin.left + "," + margin.top + ")");

        // Constructs a new cloud layout instance. It run an algorithm to find the position of words that suits your requirements
        // Wordcloud features that are different from one word to the other must be here
        var layout = d3.layout.cloud()
          .size([width, height])
          .words(parsed_words.map(function(d) { return {text: d.word, size:d.size*2.5}; }))
          .padding(5)        //space between words
          .rotate(function() { return ~~(Math.random() * 2) * 90; })
          .fontSize(function(d) { return d.size; })      // font size of words
          .on("end", draw);
        layout.start();

        // This function takes the output of 'layout' above and draw the words
        // Wordcloud features that are THE SAME from one word to the other can be here
        function draw(words) {
          svg
            .append("g")
              .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
              .selectAll("text")
                .data(words)
              .enter().append("text")
                .style("font-size", function(d) { return d.size; })
                .style("fill", "#2960c7")
                .attr("text-anchor", "middle")
                .style("font-family", "Nunito,-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,\"Helvetica Neue\",Arial,sans-serif,\"Apple Color Emoji\",\"Segoe UI Emoji\",\"Segoe UI Symbol\",\"Noto Color Emoji\"")
                .attr("transform", function(d) {
                  return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                })
                .text(function(d) { return d.text; });
        }


    }
  })
