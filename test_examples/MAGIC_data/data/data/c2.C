void c2()
{
//=========Macro generated from canvas: c2/
//=========  (Tue Feb  4 15:34:40 2020) by ROOT version 6.18/04
   TCanvas *c2 = new TCanvas("c2", "",223,78,865,658);
   c2->Range(1.313749,32.102,4.708387,35.85317);
   c2->SetFillColor(0);
   c2->SetBorderMode(0);
   c2->SetBorderSize(2);
   c2->SetLogx();
   c2->SetLogy();
   c2->SetRightMargin(0.12);
   c2->SetTopMargin(0.02);
   c2->SetFrameBorderMode(0);
   c2->SetFrameBorderMode(0);
   
   TH1F *hframe__1 = new TH1F("hframe__1","",1000,45,20000);
   hframe__1->SetMinimum(3e+32);
   hframe__1->SetMaximum(6e+35);
   hframe__1->SetDirectory(0);
   hframe__1->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   hframe__1->SetLineColor(ci);
   hframe__1->GetXaxis()->SetTitle("E [GeV]");
   hframe__1->GetXaxis()->SetLabelFont(42);
   hframe__1->GetXaxis()->SetLabelSize(0.035);
   hframe__1->GetXaxis()->SetTitleSize(0.035);
   hframe__1->GetXaxis()->SetTitleOffset(1);
   hframe__1->GetXaxis()->SetTitleFont(42);
   hframe__1->GetYaxis()->SetTitle("Integrated luminosity in 0.2 decade [erg s^{-1}]");
   hframe__1->GetYaxis()->SetLabelFont(42);
   hframe__1->GetYaxis()->SetLabelSize(0.035);
   hframe__1->GetYaxis()->SetTitleSize(0.035);
   hframe__1->GetYaxis()->SetTitleOffset(1.25);
   hframe__1->GetYaxis()->SetTitleFont(42);
   hframe__1->GetZaxis()->SetLabelFont(42);
   hframe__1->GetZaxis()->SetLabelSize(0.035);
   hframe__1->GetZaxis()->SetTitleSize(0.035);
   hframe__1->GetZaxis()->SetTitleOffset(1);
   hframe__1->GetZaxis()->SetTitleFont(42);
   hframe__1->Draw(" ");
   Double_t xAxis1[14] = {47.22056, 74.83894, 118.6108, 187.9839, 297.932, 472.1865, 748.3591, 1186.06, 1879.763, 2979.199, 4721.674, 7483.289, 11860.12, 18796.87}; 
   
   TH1F *hlum__2 = new TH1F("hlum__2","",13, xAxis1);
   hlum__2->SetBinContent(1,1.714053e+35);
   hlum__2->SetBinContent(2,3.719899e+34);
   hlum__2->SetBinContent(3,8.209042e+33);
   hlum__2->SetBinContent(4,2.881539e+33);
   hlum__2->SetBinContent(5,3.660808e+33);
   hlum__2->SetBinContent(6,1.039993e+33);
   hlum__2->SetBinContent(7,9.578809e+32);
   hlum__2->SetBinContent(8,1.796566e+33);
   hlum__2->SetBinContent(9,1.659621e+33);
   hlum__2->SetBinContent(10,2.114071e+33);
   hlum__2->SetBinContent(11,1.074671e+33);
   hlum__2->SetBinContent(12,1.300411e+33);
   hlum__2->SetBinContent(13,2.42495e+33);
   hlum__2->SetEntries(13);
   hlum__2->SetDirectory(0);
   hlum__2->SetLineWidth(2);
   hlum__2->GetXaxis()->SetLabelFont(42);
   hlum__2->GetXaxis()->SetLabelSize(0.035);
   hlum__2->GetXaxis()->SetTitleSize(0.035);
   hlum__2->GetXaxis()->SetTitleOffset(1);
   hlum__2->GetXaxis()->SetTitleFont(42);
   hlum__2->GetYaxis()->SetLabelFont(42);
   hlum__2->GetYaxis()->SetLabelSize(0.035);
   hlum__2->GetYaxis()->SetTitleSize(0.035);
   hlum__2->GetYaxis()->SetTitleFont(42);
   hlum__2->GetZaxis()->SetLabelFont(42);
   hlum__2->GetZaxis()->SetLabelSize(0.035);
   hlum__2->GetZaxis()->SetTitleSize(0.035);
   hlum__2->GetZaxis()->SetTitleOffset(1);
   hlum__2->GetZaxis()->SetTitleFont(42);
   hlum__2->Draw("XP same");
   
   Double_t _fx3001[13] = {
   59.44692,
   94.21626,
   149.3215,
   236.6567,
   375.0726,
   594.4452,
   942.1245,
   1493.155,
   2366.472,
   3750.574,
   5944.212,
   9420.865,
   14930.94};
   Double_t _fy3001[13] = {
   1.714053e+35,
   3.719899e+34,
   8.209042e+33,
   2.881539e+33,
   3.660808e+33,
   1.039993e+33,
   9.578809e+32,
   1.796566e+33,
   1.659621e+33,
   2.114071e+33,
   1.074671e+33,
   1.300411e+33,
   2.42495e+33};
   Double_t _felx3001[13] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t _fely3001[13] = {
   8.570267e+34,
   1.85995e+34,
   4.104521e+33,
   1.440769e+33,
   1.830404e+33,
   5.199963e+32,
   4.789405e+32,
   8.982831e+32,
   8.298105e+32,
   1.057036e+33,
   5.373353e+32,
   6.502054e+32,
   1.212475e+33};
   Double_t _fehx3001[13] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t _fehy3001[13] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   TGraphAsymmErrors *grae = new TGraphAsymmErrors(13,_fx3001,_fy3001,_felx3001,_fehx3001,_fely3001,_fehy3001);
   grae->SetName("");
   grae->SetTitle("");
   grae->SetFillStyle(1000);
   grae->SetLineWidth(2);
   
   TH1F *Graph_Graph3001 = new TH1F("Graph_Graph3001","",100,53.50223,16418.09);
   Graph_Graph3001->SetMinimum(4.310464e+32);
   Graph_Graph3001->SetMaximum(1.88498e+35);
   Graph_Graph3001->SetDirectory(0);
   Graph_Graph3001->SetStats(0);

   ci = TColor::GetColor("#000099");
   Graph_Graph3001->SetLineColor(ci);
   Graph_Graph3001->GetXaxis()->SetLabelFont(42);
   Graph_Graph3001->GetXaxis()->SetLabelSize(0.035);
   Graph_Graph3001->GetXaxis()->SetTitleSize(0.035);
   Graph_Graph3001->GetXaxis()->SetTitleOffset(1);
   Graph_Graph3001->GetXaxis()->SetTitleFont(42);
   Graph_Graph3001->GetYaxis()->SetLabelFont(42);
   Graph_Graph3001->GetYaxis()->SetLabelSize(0.035);
   Graph_Graph3001->GetYaxis()->SetTitleSize(0.035);
   Graph_Graph3001->GetYaxis()->SetTitleFont(42);
   Graph_Graph3001->GetZaxis()->SetLabelFont(42);
   Graph_Graph3001->GetZaxis()->SetLabelSize(0.035);
   Graph_Graph3001->GetZaxis()->SetTitleSize(0.035);
   Graph_Graph3001->GetZaxis()->SetTitleOffset(1);
   Graph_Graph3001->GetZaxis()->SetTitleFont(42);
   grae->SetHistogram(Graph_Graph3001);
   
   grae->Draw(">");
   TLine *line = new TLine(47.22056,1.967992e+35,74.83894,1.492882e+35);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(74.83894,4.271006e+34,118.6108,3.239905e+34);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(118.6108,9.425219e+33,187.9839,7.149794e+33);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(187.9839,3.308441e+33,297.932,2.509721e+33);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(297.932,4.203159e+33,472.1865,3.188438e+33);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(472.1865,1.194068e+33,748.3591,9.057979e+32);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(748.3591,1.099792e+33,1186.06,8.342814e+32);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(1186.06,2.062729e+33,1879.763,1.564748e+33);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(1879.763,1.905495e+33,2979.199,1.445473e+33);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(2979.199,2.427273e+33,4721.674,1.841284e+33);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(4721.674,1.233884e+33,7483.289,9.360012e+32);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(7483.289,1.493068e+33,11860.12,1.132613e+33);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(11860.12,2.784208e+33,18796.87,2.112048e+33);
   line->SetLineWidth(2);
   line->Draw();
   TGaxis *gaxis = new TGaxis(20000,3e+32,20000,6e+35,5.034136e-14,1.006827e-10,510,"+LG");
   gaxis->SetLabelOffset(0.005);
   gaxis->SetLabelSize(0.035);
   gaxis->SetTickSize(0.03);
   gaxis->SetGridLength(0);
   gaxis->SetTitleOffset(1.35);
   gaxis->SetTitleSize(0.04);
   gaxis->SetTitleColor(1);
   gaxis->SetTitleFont(42);
   gaxis->SetTitle("E^{2} dN/dE [erg cm^{-2} s^{-1}]");
   gaxis->SetLabelFont(42);
   gaxis->Draw();
   c2->Modified();
   c2->cd();
   c2->SetSelected(c2);
}
