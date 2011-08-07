(function () {
    'use strict';

    function Node() {
        this.p = this;
        this.c = [];
        this.q = [0, 0];
    }
    Node.prototype.parent = function (p) {
        this.p = p;
        return this;
    };
    Node.prototype.xAxis = function (x) {
        this.q[0] = x;
        return this;
    };
    Node.prototype.yAxis = function (y) {
        this.q[1] = y;
        return this;
    };
    Node.prototype.appendChild = function (d) {
        this.c.push(d.parent(this));
        return this;
    };
    Node.prototype.addTo = function (d) {
        d.appendChild(this);
        return this;
    };


    function Tree() {
        this.v = [this.newNode()];
    }
    Tree.prototype.newNode = function () {
        return new Node();
    };
    Tree.prototype.randomNode = function () {
        return this.v[Math.floor(Math.random() * this.v.length)];
    };
    Tree.prototype.addNodeAtRandom = function () {
        this.v.push(this.newNode().addTo(this.randomNode()));
        return this;
    };
    Tree.prototype.embedInPlane = function () {
        var s, i;
        s = [this.v[0]];
        i = 1;
        while (s.length > 0) {
            s.push.apply(s, s.pop().xAxis(i++).c);
        }
        s = [this.v[0]];
        i = 1;
        while (s.length > 0) {
            s.push.apply(s, s.pop().yAxis(i++).c.slice().reverse());
        }
        return this;
    };


    function Grid(args) {
        this.s = d3.select('body')
            .append('svg:svg')
            .attr('width', args.w)
            .attr('height', args.h);
        this.x = d3.scale.linear()
            .range([0, args.w])
            .domain([0, args.n]);
        this.y = d3.scale.linear()
            .range([0, args.h])
            .domain([0, args.n]);
        this.n = args.n;
        this.t = args.t;
    }
    Grid.prototype.drawSelf = function () {
        var self = this;
        var v = d3.range(this.n).map(function (i) { return [i, 0, i, self.n - 1]; });
        var h = d3.range(this.n).map(function (i) { return [0, i, self.n - 1, i]; });
        this.s.selectAll('line.grid').data(v.concat(h))
            .enter().append('svg:line') 
            .attr('class', 'grid')
            .attr('x1', function (d) { return self.x(d[0]); })
            .attr('y1', function (d) { return self.y(d[1]); })
            .attr('x2', function (d) { return self.x(d[2]); })
            .attr('y2', function (d) { return self.y(d[3]); });
        return this;
    };
    Grid.prototype.drawTree = function (t) {
        var self = this;
        var l = this.s.selectAll('line.link').data(t.v);
        l.enter().insert('svg:line', 'circle')
            .attr('class', 'link new')
            .attr('x1', function (d) { return self.x(d.q[0]); })
            .attr('y1', function (d) { return self.y(d.q[1]); })
            .attr('x2', function (d) { return self.x(d.p.q[0]); })
            .attr('y2', function (d) { return self.y(d.p.q[1]); });
        l.transition()
            .duration(this.t)
            .attr('class', 'link')
            .attr('x1', function (d) { return self.x(d.q[0]); })
            .attr('y1', function (d) { return self.y(d.q[1]); })
            .attr('x2', function (d) { return self.x(d.p.q[0]); })
            .attr('y2', function (d) { return self.y(d.p.q[1]); });
        var v = this.s.selectAll('circle.node').data(t.v);
        v.enter().insert('svg:circle')
            .attr('class', 'node new')
            .attr('cx', function (d) { return self.x(d.q[0]); })
            .attr('cy', function (d) { return self.y(d.q[1]); })
            .attr('r', '8');
        v.transition()
            .duration(this.t)
            .attr('class', 'node')
            .attr('cx', function (d) { return self.x(d.q[0]); })
            .attr('cy', function (d) { return self.y(d.q[1]); });
        return this;
    };
    Grid.prototype.randomTreeAnim = function () {
        var self = this;
        var tree = new Tree();
        this.drawTree(tree.embedInPlane());
        var intervalId = setInterval(function () {
            if (tree.v.length >= self.n - 2) {
                clearInterval(intervalId);
            } else {
                tree.addNodeAtRandom().embedInPlane();
            }
            self.drawTree(tree);
        }, 2 * this.t);
        return this;
    };


    (new Grid({w: 1024, h: 1024, n: 32, t: 1000}))
        .drawSelf()
        .randomTreeAnim();
}());
