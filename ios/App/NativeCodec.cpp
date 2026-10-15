// Compiled implementations of the audited Python decoder's array loops.
// Framing and variant dispatch remain in Python; no Apple decoder is called.
#ifdef R3D_STANDALONE_PYTHON
#include <Python.h>
#else
#include <Python/Python.h>
#endif
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <unordered_map>
#include <vector>

namespace {
using Bytes = std::vector<uint8_t>;
using Ints = std::vector<int64_t>;
void require(bool good, const char *message) { if (!good) throw std::runtime_error(message); }
struct Ref {
    PyObject *p;
    explicit Ref(PyObject *value):p(value) { if (!p) throw std::runtime_error("Python value conversion failed"); }
    ~Ref() { Py_DECREF(p); }
    Ref(const Ref &) = delete;
};
struct AllowThreads {
    PyThreadState *state;
    explicit AllowThreads(bool release):state(release ? PyEval_SaveThread() : nullptr) {}
    ~AllowThreads() { if(state)PyEval_RestoreThread(state); }
    AllowThreads(const AllowThreads &) = delete;
};
struct View {
    const uint8_t *p; size_t n;
    explicit View(PyObject *object) {
        require(PyBytes_Check(object),"Expected immutable byte array");
        p=reinterpret_cast<const uint8_t *>(PyBytes_AS_STRING(object)); n=PyBytes_GET_SIZE(object);
        require(n<=128*1024*1024,"Array exceeds 128 MiB");
    }
    uint32_t word(size_t at) const {
        require(at<=n && n-at>=4,"Truncated uint32 array");
        return uint32_t(p[at]) | uint32_t(p[at+1])<<8 | uint32_t(p[at+2])<<16 | uint32_t(p[at+3])<<24;
    }
    float real(size_t at) const { uint32_t bits=word(at); float v; std::memcpy(&v,&bits,4); return v; }
};
void word(Bytes &out,size_t at,uint32_t value) {
    require(at<=out.size() && out.size()-at>=4,"Output offset out of bounds");
    for (int k=0;k<4;++k) out[at+k]=uint8_t(value>>(8*k));
}
void real(Bytes &out,size_t at,float value) { uint32_t bits;std::memcpy(&bits,&value,4);word(out,at,bits); }
PyObject *bytes(const Bytes &out) { return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(out.data()),out.size()); }
int64_t integer(PyObject *object) {
    require(object && PyLong_Check(object),"Expected integer");
    int64_t value=PyLong_AsLongLong(object);if(PyErr_Occurred())throw std::runtime_error("Integer out of range");return value;
}
Ints integers(PyObject *object) {
    Ref seq(PySequence_Fast(object,"Expected integer sequence"));
    size_t n=PySequence_Fast_GET_SIZE(seq.p);require(n<=30000000,"Integer array exceeds limit");
    Ints out;out.reserve(n);
    for(size_t i=0;i<n;++i)out.push_back(integer(PySequence_Fast_GET_ITEM(seq.p,i)));
    return out;
}
PyObject *list(const Ints &values) {
    PyObject *out=PyList_New(values.size());if(!out)return nullptr;
    for(size_t i=0;i<values.size();++i) { PyObject *v=PyLong_FromLongLong(values[i]);if(!v){Py_DECREF(out);return nullptr;}PyList_SET_ITEM(out,i,v); }
    return out;
}
template<class F> PyObject *checked(F function) {
    try { return function(); }
    catch(const std::bad_alloc &) { return PyErr_NoMemory(); }
    catch(const std::exception &error) { if(!PyErr_Occurred())PyErr_SetString(PyExc_ValueError,error.what());return nullptr; }
}
int64_t next(int64_t c) { require(c>=0,"Negative corner");return c/3*3+(c+1)%3; }
int64_t prev(int64_t c) { require(c>=0,"Negative corner");return c/3*3+(c+2)%3; }

PyObject *entropy(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *data,*table;int width;Py_ssize_t count;
    if(!PyArg_ParseTuple(args,"OOin",&data,&table,&width,&count))return nullptr;
    require((width==8 || width==16) && count>=0 && count<=20000000,"Invalid Huff shape");
    View src(data);require(src.n%4==0,"Partial uint32 entropy word");
    struct Node { int child[2]={-1,-1};int symbol=-1; };
    std::vector<Node> nodes(1);Ref entries(PySequence_Fast(table,"Expected Huff entries"));int look=0;
    require(PySequence_Fast_GET_SIZE(entries.p)<=65536,"Too many Huff entries");
    for(Py_ssize_t i=0;i<PySequence_Fast_GET_SIZE(entries.p);++i) {
        Ints e=integers(PySequence_Fast_GET_ITEM(entries.p,i));require(e.size()==3,"Invalid Huff entry");
        int bits=int(e[1]);int64_t symbol=e[2];require(bits>=0 && bits<=32 && symbol>=0 && symbol<(1<<width),"Invalid Huff symbol/code width");
        look=std::max(look,bits);int node=0;
        for(int shift=bits-1;shift>=0;--shift) {
            require(nodes[node].symbol<0,"Huff prefix conflict");int bit=(uint64_t(e[0])>>shift)&1;
            if(nodes[node].child[bit]<0){nodes[node].child[bit]=int(nodes.size());nodes.emplace_back();}
            node=nodes[node].child[bit];
        }
        require(nodes[node].symbol<0 && nodes[node].child[0]<0 && nodes[node].child[1]<0,"Huff duplicate/prefix conflict");nodes[node].symbol=int(symbol);
    }
    require(look>0,"Constant Huff must use constant dispatch");look=std::min(10,look);
    struct Prefix {int node,used;};std::vector<Prefix> lookup(1<<look);
    for(int prefix=0;prefix<(1<<look);++prefix) {
        int node=0,used=0;
        while(used<look && nodes[node].symbol<0) {node=nodes[node].child[(prefix>>(look-used-1))&1];++used;if(node<0)break;}
        lookup[prefix]={node,used};
    }
    Bytes out(size_t(count)*(width/8));uint64_t reservoir=0;int available=0;size_t cursor=0;
    {
    AllowThreads unlocked(count>=1024);
    for(Py_ssize_t i=0;i<count;++i) {
        int node=0;
        if(available<look && cursor<src.n) {reservoir=(reservoir<<32)|src.word(cursor);available+=32;cursor+=4;}
        if(available>=look) {auto p=lookup.at(reservoir>>(available-look));node=p.node;available-=p.used;reservoir&=(uint64_t(1)<<available)-1;require(node>=0,"Unmatched entropy code");}
        while(nodes[node].symbol<0) {
            if(!available){require(cursor<src.n,"Truncated entropy");reservoir=src.word(cursor);available=32;cursor+=4;}
            --available;int bit=int(reservoir>>available);reservoir&=(uint64_t(1)<<available)-1;
            node=nodes[node].child[bit];require(node>=0,"Unmatched entropy code");
        }
        out[size_t(i)*(width/8)]=uint8_t(nodes[node].symbol);
        if(width==16)out[size_t(i)*2+1]=uint8_t(nodes[node].symbol>>8);
    }
    }
    size_t consumed=cursor*8-available;
    require(src.n==(consumed+31)/32*4,"Entropy length differs from exact consumption");
    require(reservoir==0,"Nonzero entropy padding");
    Ref packed(bytes(out));return Py_BuildValue("On",packed.p,Py_ssize_t(consumed));
}); }

PyObject *expandLane(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *values,*bitmap;int kind;Py_ssize_t count;
    if(!PyArg_ParseTuple(args,"OOin",&values,&bitmap,&kind,&count))return nullptr;
    require(kind>=1 && kind<=6 && count>0 && count<=20000000,"Invalid lane shape");
    View input(values),bits(bitmap);size_t stride=kind>=4?2:1;
    require(input.n && input.n%stride==0,"Invalid lane symbols");size_t symbols=input.n/stride;
    require(symbols<=size_t(count),"Too many lane symbols");
    auto symbol=[&](size_t at){require(at<symbols,"Not enough lane symbols");return uint32_t(input.p[at*stride])|(stride==2?uint32_t(input.p[at*2+1])<<8:0);};
    Bytes out(size_t(count)*stride);uint32_t value=symbol(0);out[0]=uint8_t(value);if(stride==2)out[1]=uint8_t(value>>8);
    if(symbols==1) {uint32_t fill=(kind==2 || kind==5)?0:value;for(Py_ssize_t i=1;i<count;++i){out[i*stride]=uint8_t(fill);if(stride==2)out[i*stride+1]=uint8_t(fill>>8);}return bytes(out);}
    require(bits.n==size_t(count+6)/8,"Invalid lane bitmap length");
    std::vector<uint32_t> table((kind==2 || kind==5)?(1<<(stride*8)):0,0);
    size_t cursor=1;int sign=0;uint32_t mask=stride==2?65535:255;
    {
    AllowThreads unlocked(count>=1024);
    for(Py_ssize_t i=0;i<count-1;++i) {
        int bit=(bits.p[i/8]>>(i%8))&1;
        if(kind==3 || kind==6){int64_t delta=symbol(cursor++);if(sign!=bit)delta=-delta;sign^=bit;value=uint32_t(int64_t(value)+delta)&mask;}
        else if(kind==1 || kind==4){if(bit)value=symbol(cursor++);}
        else {uint32_t successor;if(bit){successor=symbol(cursor++);table[value]=successor;}else successor=table[value];value=successor;}
        out[(i+1)*stride]=uint8_t(value);if(stride==2)out[(i+1)*stride+1]=uint8_t(value>>8);
    }
    }
    require(cursor==symbols,"Unused lane symbols");return bytes(out);
}); }

PyObject *quantize(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *data,*originObject,*stepObject;int channels;
    if(!PyArg_ParseTuple(args,"OOOi",&data,&originObject,&stepObject,&channels))return nullptr;
    View src(data);Ints origins=integers(originObject);Ref steps(PySequence_Fast(stepObject,"Expected steps"));
    require(channels>0 && origins.size()==size_t(channels) && PySequence_Fast_GET_SIZE(steps.p)==channels && src.n%(channels*4)==0,"Invalid quantized shape");
    for(auto origin:origins)require(origin>=INT32_MIN && origin<=INT32_MAX,"Quantized origin outside int32");
    std::vector<double> scales;for(int k=0;k<channels;++k){double step=PyFloat_AsDouble(PySequence_Fast_GET_ITEM(steps.p,k));if(PyErr_Occurred())throw std::runtime_error("Invalid step");scales.push_back(step);}
    Bytes out(src.n);
    {
    AllowThreads unlocked(src.n>=4096);
    for(size_t i=0;i<src.n/4;++i) {
        int32_t delta=int32_t(src.word(i*4));
        if(delta==-1 || delta==-2 || delta==-3) {word(out,i*4,delta==-1?0x7fc00000:delta==-2?0xff800000:0x7f800000);continue;}
        int64_t value=int64_t(delta)+origins[i%channels];require(value>=INT32_MIN && value<=INT32_MAX,"Quantized integer overflow");
        float converted=float(value);real(out,i*4,float(double(converted)*scales[i%channels]));
    }
    }
    return bytes(out);
}); }

PyObject *predictMesh(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *faceObject,*oppositeObject,*data;int channels;
    if(!PyArg_ParseTuple(args,"OOOi",&faceObject,&oppositeObject,&data,&channels))return nullptr;
    Ints faces=integers(faceObject),opposite=integers(oppositeObject);View residual(data);
    require(channels>0 && channels<=8 && residual.n%(channels*4)==0 && faces.size()%3==0 && opposite.size()==faces.size(),"Invalid predictor shape");
    size_t count=residual.n/(channels*4);std::vector<int64_t> positions(count*channels),predictor(channels,0);
    std::vector<uint8_t> assigned(count,0),seen(faces.size()/3,0);std::vector<size_t> queue;
    Bytes out(residual.n);
    {
    AllowThreads unlocked(faces.size()>=1024);
    for(auto v:faces)require(v>=0 && size_t(v)<count,"Mesh index out of range");
    auto assign=[&](size_t vertex){for(int k=0;k<channels;++k){uint32_t bits=residual.word((vertex*channels+k)*4);int32_t value=int32_t(bits);int64_t delta=(int64_t(value)>>1)^-int64_t(bits&1);int64_t q=predictor[k]+delta;require(q>=INT32_MIN && q<=INT32_MAX,"Mesh predictor integer overflow");positions[vertex*channels+k]=q;}assigned[vertex]=1;};
    for(size_t triangle=0;triangle<seen.size();++triangle) {
        if(seen[triangle])continue;size_t a=faces[3*triangle],b=faces[3*triangle+1],c=faces[3*triangle+2];
        if(!assigned[a])assign(a);
        if(!assigned[b]){for(int k=0;k<channels;++k)predictor[k]=positions[a*channels+k];assign(b);}
        if(!assigned[c]){for(int k=0;k<channels;++k)predictor[k]=(positions[a*channels+k]+positions[b*channels+k]+1)/2;assign(c);}
        queue.clear();queue.push_back(triangle);seen[triangle]=1;
        for(size_t head=0;head<queue.size();++head)for(size_t corner=queue[head]*3;corner<queue[head]*3+3;++corner) {
            int64_t other=opposite[corner];if(other==-1)continue;require(other>=0 && size_t(other)<faces.size(),"Mesh adjacency out of range");size_t vertex=faces[other];
            if(!assigned[vertex]){a=faces[next(corner)];b=faces[prev(corner)];c=faces[corner];require(assigned[a] && assigned[b] && assigned[c],"Unassigned predictor neighbor");for(int k=0;k<channels;++k)predictor[k]=positions[a*channels+k]+positions[b*channels+k]-positions[c*channels+k];assign(vertex);}
            size_t adjacent=size_t(other)/3;if(!seen[adjacent]){seen[adjacent]=1;queue.push_back(adjacent);}
        }
    }
    for(size_t i=0;i<count;++i){require(assigned[i],"Predictor did not visit every vertex");for(int k=0;k<channels;++k){int64_t v=positions[i*channels+k];require(v>=INT32_MIN && v<=INT32_MAX,"Mesh predictor integer overflow");word(out,(i*channels+k)*4,uint32_t(v));}}
    }
    return bytes(out);
}); }

PyObject *scaleFloats(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *data,*stepObject;int integerInput;
    if(!PyArg_ParseTuple(args,"OOi",&data,&stepObject,&integerInput))return nullptr;
    View src(data);Ref steps(PySequence_Fast(stepObject,"Expected scales"));size_t channels=PySequence_Fast_GET_SIZE(steps.p);
    require(channels>0 && src.n%(channels*4)==0,"Invalid scaled array");std::vector<double> scales;
    for(size_t k=0;k<channels;++k){scales.push_back(PyFloat_AsDouble(PySequence_Fast_GET_ITEM(steps.p,k)));if(PyErr_Occurred())throw std::runtime_error("Invalid scale");}
    Bytes out(src.n);for(size_t i=0;i<src.n/4;++i){float v=integerInput?float(int32_t(src.word(i*4))):src.real(i*4);real(out,i*4,float(double(v)*scales[i%channels]));}return bytes(out);
}); }

PyObject *topology(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    Py_ssize_t faceCount;PyObject *tokenObject,*integerObject;
    if(!PyArg_ParseTuple(args,"nOO",&faceCount,&tokenObject,&integerObject))return nullptr;
    require(faceCount>0 && faceCount<=10000000,"Invalid topology face count");
    View tokens(tokenObject);Ints header=integers(integerObject);int64_t corners=3*faceCount;
    require(header.size()>=4 && header[0]==0x5a4c0000,"Unknown topology header");
    require(header[1]==faceCount && (header.size()-4)%2==0,"Topology face count/pair mismatch");
    int64_t vertices=header[header.size()-2],boundaries=header.back();
    require(vertices>0 && vertices<=corners && boundaries>=0 && boundaries<=faceCount,"Invalid topology vertices/boundaries");
    Ints faces(corners,-1),opposite(corners,-1);
    {
    AllowThreads unlocked(faceCount>=1024);
    auto link=[&](int64_t a,int64_t b){require(a<corners && b<corners,"Topology link out of range");if(a>=0)opposite.at(a)=b;if(b>=0)opposite.at(b)=a;};
    for(size_t i=2;i+2<header.size();i+=2)link(header[i],header[i+1]);
    size_t bitmapBytes=(faceCount+7)/8;require(tokens.n>=bitmapBytes,"Truncated topology bitmap");
    Ints codes,starts(faceCount+1,0);codes.reserve(faceCount);int64_t depth=0,component=0;size_t extraAt=0,bitAt=0;
    if(boundaries==0)codes.push_back(8);
    while(codes.size()<size_t(faceCount)) {
        size_t at=codes.size();int code=0;
        if(tokens.p[bitAt/8]>>(bitAt%8)&1){require(bitmapBytes+extraAt/4<tokens.n,"Truncated topology tokens");code=4|((tokens.p[bitmapBytes+extraAt/4]>>(extraAt%4*2))&3);++extraAt;}
        ++bitAt;codes.push_back(code);
        if(code==7){if(depth)--depth;else{++component;if(codes.size()<size_t(faceCount)){if(component<boundaries)starts.at(component)=codes.size();else codes.push_back(8);}}}
        else if(code==4 && opposite.at(3*at+2)==-1)++depth;
    }
    require(depth==0 && codes.size()==size_t(faceCount) && component>0,"Incomplete topology component structure");
    int64_t counter=vertices-1,triangle=faceCount-1;Ints saved;
    auto closeStar=[&](int64_t corner,int64_t vertex){
        int64_t current=corner;
        for(int64_t i=0;i<=corners;++i){int64_t terminal=prev(current);faces.at(next(current))=vertex;int64_t adjacent=opposite.at(terminal);if(adjacent<0 || adjacent==corner){link(terminal,corner);return;}current=adjacent;}
        throw std::runtime_error("Nonterminating topology star");
    };
    auto readBoundary=[&](int64_t corner){
        int64_t current=next(corner);bool entered=false;
        for(int64_t i=0;i<=corners;++i){int64_t terminal=next(current),adjacent=opposite.at(terminal);if(adjacent<0){current=terminal;entered=true;break;}current=adjacent;}
        require(entered,"Nonterminating boundary entry");
        for(int64_t i=0;i<=corners;++i){
            faces.at(next(current))=counter;current=prev(current);bool ended=false;
            for(int64_t j=0;j<=corners;++j){int64_t adjacent=opposite.at(current);if(adjacent<0){ended=true;break;}current=adjacent;faces.at(next(current))=counter;current=prev(current);}
            require(ended,"Nonterminating boundary star");--counter;if(faces.at(next(current))!=-1)return;
        }
        throw std::runtime_error("Nonterminating boundary ring");
    };
    while(component>0) {
        --component;int64_t previous=-1;
        while(component>=boundaries || (component>=0 && triangle>=starts.at(component))) {
            require(triangle>=0,"Topology component underflow");int64_t corner=3*triangle,code=codes.at(triangle);
            if(code==0 || code==4 || code==6)link(previous,corner+1);
            else if(code==5)link(previous,corner+2);
            else if(code==7){if(previous>0)saved.push_back(previous);}
            else if(code==8)link(previous,corner);
            else throw std::runtime_error("Unknown topology code");
            if(code==0){closeStar(corner+2,counter);--counter;}
            else if(code==4){int64_t other=opposite.at(corner+2);if(other==-1){require(!saved.empty(),"Topology split stack underflow");link(corner+2,saved.back());saved.pop_back();}
                else if(other<=-2){link(corner+2,-other);int64_t current=corner+2;bool ended=false;
                    for(int64_t i=0;i<=corners;++i){int64_t terminal=next(current);current=opposite.at(terminal);if(current<0){readBoundary(terminal);ended=true;break;}}
                    require(ended,"Nonterminating split boundary");}}
            else if(code==8){closeStar(corner+1,counter-2);closeStar(corner+2,counter-1);closeStar(corner,counter);counter-=3;--component;}
            previous=corner;--triangle;
        }
        if(boundaries){require(component>=0,"Boundary component underflow");readBoundary(3*starts.at(component)+1);--boundaries;}
    }
    require(counter==-1,"Topology did not assign every vertex");for(auto v:faces)require(v>=0 && v<vertices,"Topology vertex out of range");
    }
    Ref f(list(faces)),o(list(opposite));return Py_BuildValue("OOL",f.p,o.p,static_cast<long long>(vertices));
}); }

Ints adjacencyFor(const Ints &faces) {
    require(faces.size()%3==0,"Invalid adjacency faces");
    struct Queue {uint64_t key=0;int64_t head=-1,tail=-1;bool used=false;};
    size_t capacity=1;while(capacity<faces.size()*2)capacity*=2;
    std::vector<Queue> pending(capacity);
    auto slot=[&](uint64_t key) -> Queue & {
        uint64_t hash=key;hash=(hash^(hash>>30))*0xbf58476d1ce4e5b9ULL;hash=(hash^(hash>>27))*0x94d049bb133111ebULL;hash^=hash>>31;
        size_t at=hash&(capacity-1);while(pending[at].used && pending[at].key!=key)at=(at+1)&(capacity-1);
        return pending[at];
    };
    Ints opposite(faces.size(),-1),following(faces.size(),-1);
    for(size_t corner=0;corner<faces.size();++corner){
        int64_t vertex=faces[corner],other=faces[next(corner)];require(vertex>=0 && vertex<=UINT32_MAX && other>=0 && other<=UINT32_MAX,"Adjacency vertex out of range");
        uint64_t key=uint64_t(vertex)<<32|uint32_t(other),reverse=uint64_t(other)<<32|uint32_t(vertex);
        auto &match=slot(reverse);
        if(match.used && match.head>=0){int64_t earlier=match.head;match.head=following[earlier];if(match.head<0)match.tail=-1;opposite[prev(earlier)]=prev(corner);opposite[prev(corner)]=prev(earlier);}
        else {auto &queue=slot(key);queue.used=true;queue.key=key;if(queue.tail<0)queue.head=corner;else following[queue.tail]=corner;queue.tail=corner;}
    }
    return opposite;
}
PyObject *adjacency(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *faces;if(!PyArg_ParseTuple(args,"O",&faces))return nullptr;Ints input=integers(faces),output;
    {AllowThreads unlocked(input.size()>=1024);output=adjacencyFor(input);}
    return list(output);
}); }

PyObject *uvIndices(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *faceObject,*oppositeObject,*maskObject,*materialObject;
    if(!PyArg_ParseTuple(args,"OOOO",&faceObject,&oppositeObject,&maskObject,&materialObject))return nullptr;
    Ints faces=integers(faceObject),opposite=integers(oppositeObject),materials=integers(materialObject);View mask(maskObject);
    require(faces.size()%3==0 && faces.size()==opposite.size(),"Invalid UV faces");size_t triangles=faces.size()/3;
    require(mask.n==(triangles+1)/2,"UV seam mask length mismatch");
    std::vector<uint8_t> seen(triangles,0);Ints indices(faces.size(),-1),faceMaterials(triangles,-1),stack;
    int64_t maximum=-1;for(auto v:faces){require(v>=0 && size_t(v)<faces.size(),"UV vertex out of range");maximum=std::max(maximum,v);}
    Ints local(maximum+1,-1);std::vector<size_t> localPatch(maximum+1,std::numeric_limits<size_t>::max());
    int64_t count=0;size_t patch=0;
    {
    AllowThreads unlocked(faces.size()>=1024);
    for(size_t seed=0;seed<triangles;++seed){
        if(seen[seed])continue;require(patch<materials.size(),"Missing UV patch material");
        stack.clear();stack.push_back(seed);seen[seed]=1;
        while(!stack.empty()){
            size_t current=stack.back();stack.pop_back();faceMaterials[current]=materials[patch];int flags=(mask.p[current/2]>>(current%2*4))&15;
            for(int edge=0;edge<3;++edge){
                size_t corner=current*3+edge;int64_t vertex=faces[corner];require(vertex>=0,"Negative UV vertex");
                if(localPatch[vertex]!=patch){localPatch[vertex]=patch;local[vertex]=count++;}indices[corner]=local[vertex];
                int64_t other=opposite[corner];if(other==-1)continue;require(other>=0 && size_t(other)<opposite.size(),"UV adjacency out of range");
                size_t adjacent=other/3;if(((flags>>edge)&1)==0 && !seen[adjacent]){seen[adjacent]=1;stack.push_back(adjacent);}
                opposite[corner]=opposite[other]=-1;
            }
        }
        ++patch;
    }
    require(patch==materials.size(),"Unused UV patch materials");
    }
    Ref i(list(indices)),m(list(faceMaterials));return Py_BuildValue("OOL",i.p,m.p,static_cast<long long>(count));
}); }

PyObject *normals(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *faceObject,*packedObject,*selectorObject;Py_ssize_t vertices,normalCount;double step;
    if(!PyArg_ParseTuple(args,"OOOnnd",&faceObject,&packedObject,&selectorObject,&vertices,&normalCount,&step))return nullptr;
    Ints faces=integers(faceObject);View packed(packedObject),selectors(selectorObject);
    require(vertices>=0 && vertices<=30000000 && normalCount>=0 && size_t(normalCount)*4==packed.n,"Invalid normal shape");
    std::vector<Ints> perVertex(vertices);Ints indices;indices.reserve(faces.size());size_t cursor=0,count=0;
    Bytes out(size_t(normalCount)*12);
    {
    AllowThreads unlocked(normalCount>=1024);
    for(auto vertex:faces){require(vertex>=0 && vertex<vertices,"Normal vertex out of range");auto &records=perVertex[vertex];int64_t index;
        if(records.empty()){records.push_back(count++);index=records[0];}
        else{require(cursor<selectors.n,"Missing normal selector");unsigned selector=selectors.p[cursor++];if(!selector){index=count++;records.push_back(index);}else{require(selector<=records.size(),"Normal selector outside vertex instances");index=records[selector-1];}}
        indices.push_back(index);
    }
    require(count==size_t(normalCount) && cursor==selectors.n,"Normal count/selector mismatch");
    uint32_t piBits=0xc0490fdb;float minusPi;std::memcpy(&minusPi,&piBits,4);float epsilon=1e-6f;
    for(size_t i=0;i<count;++i){uint32_t value=packed.word(i*4);float theta=float(double(value>>16)*step);
        float st=float(std::sin(double(theta))),ct=float(std::cos(double(theta)));
        float phi0=float(double(value&65535)*step);float phi1=float(double(phi0)/double(std::max(st,epsilon)));float phi=float(double(phi1)+double(minusPi));
        float cp=float(std::cos(double(phi))),sp=float(std::sin(double(phi)));
        real(out,i*12,float(double(cp)*double(st)));real(out,i*12+4,float(double(sp)*double(st)));real(out,i*12+8,ct);
    }
    }
    Ref n(bytes(out)),i(list(indices));return Py_BuildValue("OO",n.p,i.p);
}); }

Bytes materialFor(View attributes) {
    require(attributes.n%32==0,"Splat attributes require eight float32 channels");Bytes out(attributes.n/32*20);
    for(size_t i=0;i<attributes.n/32;++i){const int channels[]={1,2,3,0};for(int c=0;c<4;++c){float scaled=float(double(attributes.real(i*32+channels[c]*4))*255.0);double truncated=std::isfinite(scaled)?std::trunc(double(scaled)):0;double wrapped=std::fmod(truncated,256.0);out[i*20+c]=uint8_t(wrapped<0?wrapped+256:wrapped);}std::memcpy(out.data()+i*20+4,attributes.p+i*32+16,16);}
    return out;
}
PyObject *material(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *attributes;if(!PyArg_ParseTuple(args,"O",&attributes))return nullptr;View input(attributes);Bytes output;
    {AllowThreads unlocked(input.n>=4096);output=materialFor(input);}
    return bytes(output);
}); }

PyObject *field(PyObject *dictionary,const char *name) {
    require(PyDict_Check(dictionary),"Expected mesh dictionary");PyObject *value=PyDict_GetItemString(dictionary,name);require(value,"Missing mesh array");return value;
}
PyObject *validate(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *xyzObject,*attributeObject,*mesh;Py_ssize_t count;
    if(!PyArg_ParseTuple(args,"OOnO",&xyzObject,&attributeObject,&count,&mesh))return nullptr;
    View xyz(xyzObject),attributes(attributeObject),positions(field(mesh,"positions_f32")),uv(field(mesh,"uv_f32")),normals(field(mesh,"normals_f32"));
    require(count>=0 && xyz.n==size_t(count)*36 && attributes.n==size_t(count)*32,"Splat shape mismatch");
    for(size_t i=0;i<xyz.n;i+=4)require(std::isfinite(xyz.real(i)),"Nonfinite Splat position");size_t missing=0;
    for(size_t i=0;i<attributes.n/4;++i)if(!std::isfinite(attributes.real(i*4))){require(attributes.word(i*4)==0x7fc00000 && i%8>=1 && i%8<=3,"Unexpected nonfinite Splat attribute");++missing;}
    int64_t vertices=integer(field(mesh,"vertices")),uvCount=integer(field(mesh,"uvCount")),normalCount=integer(field(mesh,"normalCount")),faceCount=integer(field(mesh,"faceCount"));
    require(vertices>=0 && uvCount>=0 && normalCount>=0 && faceCount>=0,"Negative mesh size");
    require(positions.n==size_t(vertices)*12 && uv.n==size_t(uvCount)*8 && normals.n==size_t(normalCount)*12,"Mesh array shape mismatch");
    for(auto view:{positions,uv,normals})for(size_t i=0;i<view.n;i+=4)require(std::isfinite(view.real(i)),"Nonfinite mesh array");
    for(auto pair:{std::pair<const char *,int64_t>{"faces",vertices},{"uv_indices",uvCount},{"normal_indices",normalCount}}){Ints values=integers(field(mesh,pair.first));require(values.size()==size_t(faceCount)*3,"Index shape mismatch");for(auto v:values)require(v>=0 && v<pair.second,"Mesh index outside source array");}
    PyObject *out=Py_BuildValue("{s:O,s:O,s:n,s:s}","finiteGeometry",Py_True,"indexBounds",Py_True,
        "missingColorComponents",Py_ssize_t(missing),"missingColorPolicy","Preserve canonical NaNs in raw attributes; render missing RGB as zero");
    Ref owned(out);
    auto putFloat=[&](const char *key,double value){Ref v(PyFloat_FromDouble(value));if(PyDict_SetItemString(out,key,v.p)<0)throw std::runtime_error("Validation result allocation failed");};
    if(!faceCount){require(!vertices && !uvCount && !normalCount,"Nonempty arrays in empty mesh");for(auto key:{"uvMin","uvMax","normalLengthMin","normalLengthMax"})if(PyDict_SetItemString(out,key,Py_None)<0)throw std::bad_alloc();if(PyDict_SetItemString(out,"emptyMesh",Py_True)<0)throw std::bad_alloc();}
    else {
        require(uv.n && normals.n,"Missing UV/normals");double lo=std::numeric_limits<double>::infinity(),hi=-lo;
        for(size_t i=0;i<uv.n;i+=4){double v=uv.real(i);lo=std::min(lo,v);hi=std::max(hi,v);}require(lo>=-1e-6 && hi<=1.001,"UV outside original atlas");putFloat("uvMin",lo);putFloat("uvMax",hi);
        lo=std::numeric_limits<double>::infinity();hi=-lo;
        for(size_t i=0;i<normals.n;i+=12){double x=normals.real(i),y=normals.real(i+4),z=normals.real(i+8);double length=std::sqrt((x*x+y*y)+z*z);lo=std::min(lo,length);hi=std::max(hi,length);}require(lo>=.99999 && hi<=1.00001,"Invalid mesh normal length");putFloat("normalLengthMin",lo);putFloat("normalLengthMax",hi);
    }
    Py_INCREF(out);return out;
}); }

PyObject *packMobile(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *xyzObject,*attributeObject,*mesh;
    if(!PyArg_ParseTuple(args,"OOO",&xyzObject,&attributeObject,&mesh))return nullptr;
    // Retain dictionary values while another Python thread can mutate the dictionary.
    Ref positionData(Py_NewRef(field(mesh,"positions_f32"))),normalData(Py_NewRef(field(mesh,"normals_f32"))),uvData(Py_NewRef(field(mesh,"uv_f32")));
    View xyz(xyzObject),attributes(attributeObject),positions(positionData.p),normals(normalData.p),uv(uvData.p);
    Ints faces=integers(field(mesh,"faces")),uvIndices=integers(field(mesh,"uv_indices")),normalIndices=integers(field(mesh,"normal_indices"));
    require(xyz.n%36==0 && attributes.n/32==xyz.n/36 && attributes.n%32==0 && faces.size()==uvIndices.size() && faces.size()==normalIndices.size(),"Invalid mobile packing shape");
    require(faces.size()<=1500000 && xyz.n/36<=500000,"Tile geometry budget exceeded");
    struct Key {int64_t p,t,n;bool operator==(const Key &v)const{return p==v.p && t==v.t && n==v.n;}};
    struct Hash {size_t operator()(const Key &v)const{return size_t(v.p)*73856093 ^ size_t(v.t)*19349663 ^ size_t(v.n)*83492791;}};
    std::unordered_map<Key,uint32_t,Hash> unique;unique.reserve(faces.size());Bytes vertices,indices(faces.size()*4),splats;vertices.reserve(faces.size()*32);
    std::array<double,3> lower,upper;
    {
    AllowThreads unlocked(faces.size()>=1024 || xyz.n>=4096);
    for(size_t i=0;i<faces.size();++i){Key key{faces[i],uvIndices[i],normalIndices[i]};require(key.p>=0 && size_t(key.p)<positions.n/12 && key.t>=0 && size_t(key.t)<uv.n/8 && key.n>=0 && size_t(key.n)<normals.n/12,"Packing index out of bounds");
        auto inserted=unique.emplace(key,uint32_t(unique.size()));uint32_t index=inserted.first->second;
        if(inserted.second){size_t at=vertices.size();vertices.resize(at+32);std::memcpy(vertices.data()+at,positions.p+key.p*12,12);std::memcpy(vertices.data()+at+12,normals.p+key.n*12,12);std::memcpy(vertices.data()+at+24,uv.p+key.t*8,8);}word(indices,i*4,index);
    }
    Bytes colors=materialFor(attributes);splats.reserve(xyz.n/12*40);
    for(size_t i=0;i<xyz.n/36;++i){if(!colors[i*20+3])continue;for(int corner=0;corner<3;++corner){size_t at=splats.size();splats.resize(at+40);std::memcpy(splats.data()+at,xyz.p+i*36+corner*12,12);for(int k=0;k<4;++k)real(splats,at+12+k*4,float(double(colors[i*20+k])/255.0));for(int k=0;k<3;++k)real(splats,at+28+k*4,k==corner?1.0f:0.0f);}}
    lower.fill(std::numeric_limits<double>::infinity());upper.fill(-std::numeric_limits<double>::infinity());
    require(positions.n || xyz.n,"Missing geometry");
    for(auto view:{positions,xyz}){require(view.n%12==0,"Invalid position shape");for(size_t i=0;i<view.n;i+=12)for(int k=0;k<3;++k){double v=view.real(i+k*4);require(std::isfinite(v),"Nonfinite geometry");lower[k]=std::min(lower[k],v);upper[k]=std::max(upper[k],v);}}
    }
    Ref v(bytes(vertices)),i(bytes(indices)),s(bytes(splats));Ref lo(Py_BuildValue("[ddd]",lower[0],lower[1],lower[2])),hi(Py_BuildValue("[ddd]",upper[0],upper[1],upper[2]));
    return Py_BuildValue("OOOOOn",v.p,i.p,s.p,lo.p,hi.p,Py_ssize_t(unique.size()));
}); }

PyObject *decodeHuff(PyObject *,PyObject *args) { return checked([&]() -> PyObject * {
    PyObject *data;int width;Py_ssize_t count;
    if(!PyArg_ParseTuple(args,"Oin",&data,&width,&count))return nullptr;
    require((width==8 || width==16) && count>=0 && count<=20000000,"Invalid Huff shape");View src(data);
    require(src.n>=4 && (src.word(0)&0x7f0000ff)==0x61000002,"Invalid Huff marker");
    if(src.word(0)&0x80000000){require(src.n==4+size_t(count)*(width/8),"Literal Huff length mismatch");Ref out(PyBytes_FromStringAndSize(reinterpret_cast<const char *>(src.p+4),src.n-4));return Py_BuildValue("O{s:s,s:n}",out.p,"mode","literal","count",count);}
    size_t position=0;
    auto read=[&](unsigned n){require(n<=32 && position+n<=(src.n-4)*8,"Truncated Huff table");uint32_t out=0;unsigned left=n;while(left){size_t at=position/32;unsigned offset=position%32,take=std::min(left,32-offset);uint32_t value=src.word(4+at*4);uint64_t mask=(uint64_t(1)<<take)-1;out=uint32_t((uint64_t(out)<<take)|((value>>(32-offset-take))&mask));position+=take;left-=take;}return out;};
    unsigned n=read(width)+1,lenWidth=read(3);uint32_t symbol=0;Ref entries(PyList_New(n)),lengths(PyDict_New());unsigned zeroCodes=0,constant=0;
    for(unsigned i=0;i<n;++i){unsigned bits,code;if(lenWidth){bits=read(lenWidth)+1;code=read(bits);}else{bits=n==2?1:0;code=n==2?read(1):0;}
        if(read(1)){if(read(1))symbol=read(width);else symbol+=read(width/2);}
        require(symbol<unsigned(1<<width),"Huff symbol exceeds width");PyObject *entry=Py_BuildValue("(III)",code,bits,symbol);if(!entry)throw std::bad_alloc();PyList_SET_ITEM(entries.p,i,entry);
        if(!bits){++zeroCodes;constant=symbol;}
        Ref key(PyLong_FromUnsignedLong(bits));PyObject *old=PyDict_GetItem(lengths.p,key.p);long total=old?PyLong_AsLong(old):0;Ref value(PyLong_FromLong(total+1));if(PyDict_SetItem(lengths.p,key.p,value.p)<0)throw std::bad_alloc();
        ++symbol;if(i!=n-1)require(symbol<=unsigned(1<<width),"Huff symbol range exceeds width");
    }
    size_t tableBits=position,aligned=(position+31)/32*4;require(4+aligned<=src.n,"Huff table alignment exceeds input");
    Ref payload(PyBytes_FromStringAndSize(reinterpret_cast<const char *>(src.p+4+aligned),src.n-4-aligned));Py_ssize_t consumed=0;PyObject *output;
    if(zeroCodes){require(n==1 && src.n==4+aligned,"Invalid constant Huff entropy");Bytes out(size_t(count)*(width/8));for(Py_ssize_t i=0;i<count;++i){out[i*(width/8)]=uint8_t(constant);if(width==16)out[i*2+1]=uint8_t(constant>>8);}output=bytes(out);}
    else {Ref entropyArgs(Py_BuildValue("(OOin)",payload.p,entries.p,width,count));Ref result(entropy(nullptr,entropyArgs.p));PyObject *packed=nullptr;if(!PyArg_ParseTuple(result.p,"On",&packed,&consumed))throw std::runtime_error("Invalid entropy result");output=packed;Py_INCREF(output);}
    Ref packed(output);
    Ref stats(Py_BuildValue("{s:s,s:n,s:I,s:I,s:n,s:n,s:O,s:n,s:n}","mode","compressed","count",count,
        "symbols",n,"codeLengthWidth",lenWidth,"tableBits",Py_ssize_t(tableBits),"alignedBytes",Py_ssize_t(aligned),
        "lengths",lengths.p,"entropyBitsConsumed",consumed,"entropyPaddingBits",Py_ssize_t((src.n-4-aligned)*8)-consumed));
    if(zeroCodes && PyDict_DelItemString(stats.p,"entropyBitsConsumed")<0)throw std::runtime_error("Invalid constant Huff statistics");
    return Py_BuildValue("OO",packed.p,stats.p);
}); }

PyMethodDef methods[] = {
    {"decode_huff",decodeHuff,METH_VARARGS,nullptr},
    {"entropy",entropy,METH_VARARGS,nullptr},{"expand_lane",expandLane,METH_VARARGS,nullptr},
    {"quantize",quantize,METH_VARARGS,nullptr},{"predict_mesh",predictMesh,METH_VARARGS,nullptr},
    {"scale_floats",scaleFloats,METH_VARARGS,nullptr},{"topology",topology,METH_VARARGS,nullptr},
    {"adjacency",adjacency,METH_VARARGS,nullptr},{"uv_indices",uvIndices,METH_VARARGS,nullptr},
    {"normals",normals,METH_VARARGS,nullptr},{"material20",material,METH_VARARGS,nullptr},
    {"validate",validate,METH_VARARGS,nullptr},{"pack_mobile",packMobile,METH_VARARGS,nullptr},
    {nullptr,nullptr,0,nullptr}
};
PyModuleDef module={PyModuleDef_HEAD_INIT,"_r3d_accel",nullptr,-1,methods};
}
extern "C" PyObject *PyInit__r3d_accel() { return PyModule_Create(&module); }
